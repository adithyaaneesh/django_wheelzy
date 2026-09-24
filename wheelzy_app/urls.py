from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
     # ================= AUTH =================
    path("register/", views.register, name="register"),
    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("resend-otp/", views.resend_otp, name="resend_otp"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # ================= HOME & PROFILE =================
    path("", views.splash, name="splash"),
    path("home/", views.home, name="home"),
    path("profile/", views.profile_view, name="profile"),
    path("profile/edit/", views.edit_profile, name="edit_profile"),

    # ================= VEHICLES (CUSTOMER) =================
    path("all_vehicles/", views.all_vehicle, name="all_vehicles"),
    path("vehicle/<int:id>/", views.vehicle_details, name="vehicle_details"),
    path("booking/<int:vehicle_id>/", views.book_vehicle, name="book_vehicle"),
    path("payment/<int:booking_id>/", views.payment_page, name="payment_page"),


    # ================= BOOKINGS (CUSTOMER) =================
    path("my_bookings/", views.my_bookings, name="my_bookings"),
    path("booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("booking/<int:booking_id>/in-use/", views.mark_in_use, name="mark_in_use"),


    # ================= OWNER =================
    path("owner_dashboard/", views.owner_dashboard, name="owner_dashboard"),
    path("edit-profile/", views.edit_owner_profile, name="edit_owner_profile"),
    path("owner_vehicle_list/", views.owner_vehicles, name="owner_vehicle_list"),
    path("owner_vehicle_bookings/", views.owner_bookings, name="owner_vehicle_bookings"),
    path('my-vehicle-damages/', views.owner_damage_list, name='owner_damage_list'),
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

    path("admin_revenue/", views.admin_revenue, name="admin_revenue"),
    path("admin_analytics/", views.admin_analytics, name="admin_analytics"),

    # ================= DAMAGE REPORTS =================
    path("booking/<int:booking_id>/damage-report/",views.owner_add_damage_report,name="add_damage_report"),
    path("admin_damage-reports/",views.admin_damage_report_list,name="admin_damage_report_list"),
    path("admin_damage-report/<int:report_id>/",views.admin_damage_report_detail,name="admin_damage_report_detail"),

    path("damage-report/<int:report_id>/pay/",views.pay_damage_charge,name="pay_damage_charge"),
    path("customer_damage_detail/<int:booking_id>/",views.customer_damage_detail,name="customer_damage_detail"),

    path("admin_damage/<int:booking_id>/",views.admin_damage_details,name="admin_damage_details"),

    path("admin/damage/paid/<int:damage_id>/",views.mark_damage_paid,name="mark_damage_paid"),


    # ================= NOTIFICATIONS =================
    path("notifications/", views.notifications_view, name="notifications"),
    path("notifications/mark-all-read/", views.mark_all_notifications_read, name="mark_all_notifications_read"),
    path("notifications/clear-read/", views.clear_read_notifications, name="clear_read_notifications"),
    path("notifications/mark-read/", views.mark_notification_read, name="mark_notification_read"),
    path("notifications/unread-count/", views.unread_notification_count, name="unread_notification_count"),


    path("admin_booking/<int:booking_id>/details/",views.admin_booking_details,name="admin_booking_details"),
    path("payment/<int:booking_id>/", views.payment_page, name="payment_page"),
    path("razorpay/verify/", views.razorpay_verify, name="razorpay_verify"),

    path("damage-payment/verify/",views.verify_damage_payment,name="verify_damage_payment"),
    path("payment/cancelled/<int:booking_id>/",views.payment_cancelled,name="payment_cancelled"),
    path("booking/<int:booking_id>/reject/", views.reject_booking, name="reject_booking"),

    path("admin-panel/refunds/", views.admin_refund_list, name="admin_refund_list"),
    path("admin_refund/<int:refund_id>/", views.admin_refund_detail, name="admin_refund_detail"),
    path("booking/<int:booking_id>/return-photos/", views.upload_return_photos, name="upload_return_photos"),



]


if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
