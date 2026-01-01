from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     # ================= AUTH =================
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ================= HOME & PROFILE =================
    path("", views.home, name="home"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # ================= VEHICLES (CUSTOMER) =================
    path("all_vehicles/", views.all_vehicle, name="all_vehicles"),
    path("vehicle/<int:id>/", views.vehicle_details, name="vehicle_details"),
    path("booking/<int:vehicle_id>/", views.book_vehicle, name="book_vehicle"),

    # ================= BOOKINGS (CUSTOMER) =================
    path("my_bookings/", views.my_bookings, name="my_bookings"),
    path("booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("booking/<int:booking_id>/in-use/", views.mark_in_use, name="mark_in_use"),

    # ================= OWNER =================
    path("owner_dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("owner_vehicle_list/", views.owner_vehicles, name="owner_vehicle_list"),
    path("owner_vehicle_bookings/", views.owner_bookings, name="owner_vehicle_bookings"),

    path("vehicle/add/", views.add_vehicle, name="add_vehicle"),
    path("vehicle/update/<int:id>/", views.update_vehicle, name="update_vehicle"),
    path("vehicle/delete/<int:id>/", views.delete_vehicle, name="delete_vehicle"),
    path("booking/<int:booking_id>/handover-photos/",views.upload_handover_photos,name="upload_handover_photos"),

    # ================= ADMIN =================
    path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin_users/", views.admin_users, name="admin_users"),

    path("admin_vehicles/", views.admin_vehicles, name="admin_vehicles"),
    path("admin_vehicles/add/", views.admin_add_vehicle, name="admin_add_vehicle"),
    path("admin_vehicles/update/<int:id>/", views.admin_update_vehicle, name="admin_update_vehicle"),
    path("admin_vehicles/delete/<int:id>/", views.admin_delete_vehicle, name="admin_delete_vehicle"),

    path("admin_bookings/", views.admin_bookings, name="admin_bookings"),
    path("booking/<int:booking_id>/approve/", views.approve_booking, name="approve_booking"),
    path("booking/<int:booking_id>/returned/", views.mark_returned, name="mark_returned"),

    path("admin_damages/", views.admin_damage_reports, name="admin_damage_reports"),
    path("admin_revenue/", views.admin_revenue, name="admin_revenue"),
    path("admin_analytics/", views.admin_analytics, name="admin_analytics"),

    # ================= DAMAGE REPORTS =================
    path("booking/<int:booking_id>/damage-report/",views.add_damage_report,name="add_damage_report"),

    # Admin damage reports
    path("admin_damage-reports/",views.admin_damage_report_list,name="admin_damage_report_list"),
    path("admin_damage-report/<int:report_id>/",views.admin_damage_report_detail,name="admin_damage_report_detail"),

    # Customer damage reports
    # path("my_damage-reports/",views.customer_damage_reports,name="customer_damage_reports"),
    path("damage-report/<int:report_id>/pay/",views.pay_damage_charge,name="pay_damage_charge"),
    path("customer_damage_detail/<int:booking_id>/",views.customer_damage_detail,name="customer_damage_detail"),


    # ================= NOTIFICATIONS =================
    path("notifications/", views.notifications_view, name="notifications"),
]


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# from django.urls import path
# from django.conf import settings
# from django.conf.urls.static import static

# from . import views

# urlpatterns = [

#     # ================= AUTH =================
#     path("register/", views.register, name="register"),
#     path("login/", views.login_view, name="login"),
#     path("logout/", views.logout_view, name="logout"),

#     # ================= HOME & PROFILE =================
#     path("", views.home, name="home"),
#     path("profile/", views.profile_view, name="profile"),
#     path("profile/edit/", views.edit_profile, name="edit_profile"),

#     # ================= VEHICLES (CUSTOMER) =================
#     path("vehicles/", views.all_vehicle, name="all_vehicles"),
#     path("vehicle/<int:id>/", views.vehicle_details, name="vehicle_details"),
#     path("vehicle/<int:vehicle_id>/book/", views.book_vehicle, name="book_vehicle"),

#     # ================= BOOKINGS (CUSTOMER) =================
#     path("my-bookings/", views.my_bookings, name="my_bookings"),
#     path("booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
#     path("booking/<int:booking_id>/in-use/", views.mark_in_use, name="mark_in_use"),

#     # ================= OWNER =================
#     path("owner_dashboard/", views.owner_dashboard, name="owner_dashboard"),
#     path("owner_vehicles/", views.owner_vehicles, name="owner_vehicle_list"),
#     path("owner_bookings/", views.owner_bookings, name="owner_vehicle_bookings"),

#     path("owner_booking/<int:booking_id>/handover-photos/",views.upload_handover_photos,name="upload_handover_photos"),

#     path("owner_booking/<int:booking_id>/damage-report/",views.owner_add_damage_report,name="add_damage_report"),

#     # ================= ADMIN =================
#     path("admin_dashboard/", views.admin_dashboard, name="admin_dashboard"),
#     path("admin_users/", views.admin_users, name="admin_users"),
#     path("admin_vehicles/", views.admin_vehicles, name="admin_vehicles"),
#     path("admin_bookings/", views.admin_bookings, name="admin_bookings"),

#     path("admin_booking/<int:booking_id>/approve/",views.approve_booking,name="approve_booking"),

#     path("admin_booking/<int:booking_id>/returned/",views.mark_returned,name="mark_returned"),

#     # ================= DAMAGE REPORTS =================
#     path("admin_damage-reports/",views.admin_damage_report_list,name="admin_damage_report_list"),

#     path("admin_damage-report/<int:report_id>/",views.admin_damage_report_detail,name="admin_damage_report_detail"),

#     path("customer_booking/<int:booking_id>/damage/",views.customer_damage_detail,name="customer_damage_detail"),

#     path("damage-report/<int:report_id>/pay/",views.pay_damage_charge,name="pay_damage_charge"),

#     # ================= NOTIFICATIONS =================
#     path("notifications/", views.notifications_view, name="notifications"),
# ]


# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
