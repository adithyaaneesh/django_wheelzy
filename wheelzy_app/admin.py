from django.contrib import admin
from .models import DamagePhoto, Vehicle, Booking, DamageReport, UserProfile, Notification, VehicleHandoverPhoto
# Register your models here.

admin.site.register(Vehicle)
admin.site.register(Booking)
admin.site.register(DamageReport)
admin.site.register(DamagePhoto)
admin.site.register(UserProfile)
admin.site.register(Notification)
admin.site.register(VehicleHandoverPhoto)