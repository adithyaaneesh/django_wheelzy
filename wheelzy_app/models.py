from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


# =========================
# USER PROFILE
# =========================
class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


# =========================
# VEHICLE
# =========================
class Vehicle(models.Model):
    VEHICLE_TYPES = (
        ("car", "Car"),
        ("bike", "Bike"),
    )

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="vehicles",
        null=True,
        blank=True
    )

    vehicle_name = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=25, choices=VEHICLE_TYPES)
    number_plate = models.CharField(max_length=50, unique=True)
    price_per_hour = models.PositiveIntegerField()
    seats = models.PositiveIntegerField(blank=True)
    image = models.ImageField(upload_to="vehicles/", null=True, blank=True)

    is_available = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Auto-assign seats if not provided
        if not self.seats:
            self.seats = 4 if self.vehicle_type == "car" else 2
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle_name} ({self.number_plate})"


# =========================
# BOOKING
# =========================


class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_use', 'In Use'),
        ('returned', 'Completed'),
        ('damage_reported', 'Damage Reported'),
        ('cancelled', 'Cancelled'),
    )



    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings",null=True, blank=True
    )

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name="bookings", null=True, blank=True
    )

    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    ordered_at = models.DateTimeField(auto_now_add=True)
    def can_user_book(user):
        return not DamageReport.objects.filter(
            booking__user=user,
            is_paid=False
        ).exists()


    def calculate_price(self):
        hours = (self.end_time - self.start_time).total_seconds() / 3600
        return round(hours * self.vehicle.price_per_hour, 2)

    def save(self, *args, **kwargs):
        # Calculate price ONLY on first creation
        if not self.pk:
            self.total_price = self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.id} - {self.vehicle.vehicle_name}"


# =========================
# NOTIFICATION
# =========================
class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification → {self.user.username}"


# =========================
# VEHICLE HANDOVER PHOTOS
# =========================
class VehicleHandoverPhoto(models.Model):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="handover_photos",
        null=True,
        blank=True
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="handover_photos",
        blank=True,
        null=True
    )

    image = models.ImageField(upload_to="handover_photos/")
    created_at = models.DateTimeField(auto_now_add=True)



# =========================
# DAMAGE REPORT
# =========================
class DamageReport(models.Model):
    booking = models.OneToOneField( Booking,on_delete=models.CASCADE,related_name="damage_report")
    vehicle = models.ForeignKey(Vehicle,on_delete=models.CASCADE,related_name="damage_reports",null=True,blank=True)
    reported_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="reported_damages")
    description = models.TextField()
    extra_charge = models.DecimalField(max_digits=8,decimal_places=2,default=0)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Damage Report #{self.id} - Booking #{self.booking.id}"


# =========================
# DAMAGE PHOTOS
# =========================
class DamagePhoto(models.Model):
    report = models.ForeignKey(
        DamageReport,
        on_delete=models.CASCADE,
        related_name="photos"
    )
    image = models.ImageField(upload_to="damage_photos/")

    def __str__(self):
        return f"Damage Photo - Report #{self.report.id}"
