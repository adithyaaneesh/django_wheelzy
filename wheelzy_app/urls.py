from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path('', views.home, name="home"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    path('all_vehicles', views.all_vehicle, name="all_vehicles"),
    path("my_bookings/", views.my_bookings, name="my_bookings"),

    path("owner_dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("owner_vehicle_list/", views.owner_vehicles, name="owner_vehicle_list"),
    path("owner_vehicle_bookings/", views.owner_bookings, name="owner_vehicle_bookings"),
    path('add/', views.add_vehicle, name="add_vehicle"),
    path('update/<int:id>/', views.update_vehicle, name="update_vehicle"),
    path('delete/<int:id>/', views.delete_vehicle, name="delete_vehicle"),
    path('vehicle_details/<int:id>/', views.vehicle_details, name="vehicle_details"),
    path('booking/<int:vehicle_id>/', views.book_vehicle, name="book_vehicle"),

    path("admin_vehicles/add/", views.admin_add_vehicle, name="admin_add_vehicle"),
    path("admin_vehicles/update/<int:id>/", views.admin_update_vehicle, name="admin_update_vehicle"),
    path("admin_vehicles/delete/<int:id>/", views.admin_delete_vehicle, name="admin_delete_vehicle"),
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin_users/", views.admin_users, name="admin_users"),
    path("admin_vehicles/", views.admin_vehicles, name="admin_vehicles"),

    path("admin_bookings/", views.admin_bookings, name="admin_bookings"),
    path("booking/<int:booking_id>/approve/", views.approve_booking, name="approve_booking"),
    path("booking/<int:booking_id>/in-use/", views.mark_in_use, name="mark_in_use"),
    path("booking/<int:booking_id>/returned/", views.mark_returned, name="mark_returned"),
    path("booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),

    
    path("admin_damages/", views.admin_damage_reports, name="admin_damage_reports"),
    path("admin_revenue/", views.admin_revenue, name="admin_revenue"),
    path("admin_analytics/", views.admin_analytics, name="admin_analytics"),
    path("admin/vehicles/delete/<int:id>/", views.admin_delete_vehicle, name="admin_delete_vehicle"),




    # path('payment_page/', views.vehicle_details, name="payment_page"),
]


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)