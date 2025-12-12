from django.db import models

# Create your models here.
class Vehicle(models.Model):
    VEHICLE_TYPES =(
        ('car','Car'),
        ('bike','Bike'),
    )
    vehicle_name = models.CharField(max_length=255)
    vehicle_type = models.CharField(max_length=25, choices=VEHICLE_TYPES)
    number_plate = models.CharField(max_length=50, unique=True)
    price_per_hour = models.PositiveIntegerField()
    image = models.ImageField(null=True, blank=True)
    is_available = models.BooleanField(default=True)

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
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS, default="pending")
    ordered_at = models.DateTimeField(auto_now_add=True)

    def calculate_price(self):
        hours = (self.end_time - self.start_time).total_seconds() / 3600
        price = hours * float(self.vehicle.price_per_hour)
        return round(price, 2)

    def save(self, *args, **kwargs):
        self.total_price = self.calculate_price()
        self.security_deposit = 2000 
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