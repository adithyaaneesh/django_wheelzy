from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name="home"),
    path('add/', views.add_vehicle, name="add_vehicle"),
    path('delete/<int:id>/', views.delete_vehicle, name="delete_vehicle"),
    path('vehicle_details/', views.vehicle_details, name="vehicle_details"),
    # path('payment_page/', views.vehicle_details, name="payment_page"),
]


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)