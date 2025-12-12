from django.contrib import admin
from .models import Vehicle, Booking, DamageReport
# Register your models here.

admin.site.register(Vehicle)
admin.site.register(Booking)
admin.site.register(DamageReport)