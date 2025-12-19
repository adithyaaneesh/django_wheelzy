from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15)
    address = models.TextField()

    def __str__(self):
        return self.user.username
    
    
class Vehicle(models.Model):
    VEHICLE_TYPES = (
        ('car', 'Car'),
        ('bike', 'Bike'),
    )

    # 👤 Owner of the vehicle
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
    seats = models.PositiveIntegerField(help_text="Number of seats", blank=True)
    image = models.ImageField(upload_to="vehicles/", null=True, blank=True)

    def save(self, *args, **kwargs):
        # Auto assign seats
        if not self.seats:
            if self.vehicle_type == "car":
                self.seats = 4
            elif self.vehicle_type == "bike":
                self.seats = 2
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle_name} - {self.number_plate}"


class Booking(models.Model):
    STATUS = (
        ("pending", "Pending Payment"),
        ("confirmed", "Confirmed"),
        ("in_use", "In Use"),
        ("returned", "Returned"),
        ("cancelled", "Cancelled"),
    )

    # 👤 Customer who booked
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    security_deposit = models.PositiveIntegerField(default=2000)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    ordered_at = models.DateTimeField(auto_now_add=True)

    def calculate_price(self):
        hours = (self.end_time - self.start_time).total_seconds() / 3600
        return round(hours * self.vehicle.price_per_hour, 2)

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_price()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking #{self.id} - {self.vehicle.vehicle_name}"


class DamageReport(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    damage_description = models.TextField(blank=True)
    damage_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    images = models.ImageField(upload_to="damage/", null=True, blank=True)

    def __str__(self):
        return f"Damage Report for Booking #{self.booking.id}"
