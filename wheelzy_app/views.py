from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import DamagePhoto, Vehicle, Booking, DamageReport, UserProfile, Notification, VehicleHandoverPhoto
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import models
from django.db.models import Prefetch
from django.http import JsonResponse
from django.views.decorators.http import require_POST


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        role = request.POST.get("role")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        photo = request.FILES.get("photo") 

        if not all([username, email, password, cpassword, phone, address, photo]):
            messages.error(request, "All fields are required")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        if password != cpassword:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        UserProfile.objects.create(
            user=user,
            phone_number=phone,
            address=address,
            photo=photo
        )

        if role == "owner":
            owner_group, _ = Group.objects.get_or_create(name="owner")
            user.groups.add(owner_group)

        messages.success(request, "Registration successful!")
        return redirect("login")

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        selected_role = request.POST.get("role")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect("login")

        # -------- ADMIN --------
        if selected_role == "admin":
            if not user.is_superuser:
                messages.error(request, "You are not an admin")
                return redirect("login")

            login(request, user)
            return redirect("admin_dashboard")

        # -------- OWNER --------
        elif selected_role == "owner":
            if user.is_superuser or not user.groups.filter(name="owner").exists():
                messages.error(request, "You are not registered as an owner")
                return redirect("login")

            login(request, user)
            return redirect("owner_dashboard")

        # -------- CUSTOMER --------
        elif selected_role == "customer":
            if user.is_superuser or user.groups.filter(name="owner").exists():
                messages.error(request, "Admins and Owners cannot login as customers")
                return redirect("login")

            login(request, user)
            return redirect("home")

        else:
            messages.error(request, "Invalid role selected")
            return redirect("login")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    return redirect("login")



def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect("admin_dashboard")
        if request.user.groups.filter(name="owner").exists():
            return redirect("owner_dashboard")

    vehicles = Vehicle.objects.all()
    active_bookings = Booking.objects.filter(
        status__in=["pending", "confirmed", "in_use"]
    ).values_list("vehicle_id", flat=True)

    profile = None
    unread_count = 0
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        unread_count = get_unread_notification_count(request.user)


    return render(request, "home.html", {
        "vehicles": vehicles,
        "booked_vehicle_ids": active_bookings,
        "profile": profile,
        "unread_count": unread_count,

    })



@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(request, "profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    if request.method == "POST":
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        new_username = request.POST.get("username")
        if new_username and new_username != request.user.username:
            if User.objects.filter(username=new_username).exists():
                messages.error(request, "Username already exists")
                return redirect("profile")
            request.user.username = new_username

        request.user.email = request.POST.get("email")
        profile.phone_number = request.POST.get("phone")
        profile.address = request.POST.get("address")

        if request.FILES.get("photo"):
            profile.photo = request.FILES["photo"]

        request.user.save()
        profile.save()

        messages.success(request, "Profile updated successfully")
        return redirect("profile")

    return redirect("profile")



@login_required
def all_vehicle(request):
    vehicles = Vehicle.objects.all()

    search_query = request.GET.get("q")
    vehicle_type = request.GET.get("type")
    seats = request.GET.get("seats")
    available = request.GET.get("available")
    if search_query:
        vehicles = vehicles.filter(vehicle_name__icontains=search_query) | \
                   vehicles.filter(number_plate__icontains=search_query)
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)
    if seats:
        vehicles = vehicles.filter(seats=seats)
    booked_vehicle_ids = Booking.objects.filter(
        status__in=["pending", "confirmed", "in_use"]
    ).values_list("vehicle_id", flat=True)
    if available == "1":
        vehicles = vehicles.exclude(id__in=booked_vehicle_ids)

    return render(request, "vehicle_list.html", {
        "vehicles": vehicles,
        "booked_vehicle_ids": booked_vehicle_ids
    })

@login_required
def vehicle_details(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)

    is_booked = Booking.objects.filter(
        vehicle=vehicle,
        status__in=["pending", "confirmed", "in_use"]
    ).exists()

    return render(request, "vehicle_detail.html", {
        "vehicle": vehicle,
        "is_booked": is_booked
    })


@login_required
def book_vehicle(request, vehicle_id):
    if DamageReport.objects.filter(
        booking__user=request.user,
        is_paid=False
    ).exists():
        messages.error(
            request,
            "You have unpaid damage charges. Please complete payment before booking another vehicle."
        )
        return redirect("my_bookings")
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    owner = vehicle.owner
    owner_profile = None
    if owner:
        owner_profile = getattr(owner, "profile", None)
    if vehicle.owner == request.user:
        messages.error(request, "You cannot book your own vehicle")
        return redirect("vehicle_details", vehicle.id)
    if request.method == "POST":
        start_time = request.POST.get("start_time")
        end_time = request.POST.get("end_time")
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
        if end <= start:
            messages.error(request, "End time must be after start time")
            return redirect("book_vehicle", vehicle.id)
        if Booking.objects.filter(
            vehicle=vehicle,
            status__in=["pending", "confirmed", "in_use"]
        ).exists():
            messages.error(request, "This vehicle is already booked")
            return redirect("vehicle_details", vehicle.id)
        Booking.objects.create(
            user=request.user,
            vehicle=vehicle,
            start_time=start,
            end_time=end,
            status="pending"
        )
        if vehicle.owner:
            Notification.objects.create(
                user=vehicle.owner,
                message=f"New booking request for {vehicle.vehicle_name}. Upload handover photos."
            )
        messages.success(request, "Booking created successfully!")
        return redirect("home")
    return render(
        request,
        "booking_form.html",
        {
            "vehicle": vehicle,
            "owner": owner,
            "owner_profile": owner_profile
        }
    )

@login_required
def my_bookings(request):
    bookings = (
        Booking.objects
        .filter(user=request.user)
        .select_related("vehicle", "damage_report")
        .order_by("-ordered_at")
    )

    has_unpaid_damage = DamageReport.objects.filter(
        booking__user=request.user,
        is_paid=False
    ).exists()

    return render(
        request,
        "my_bookings.html",
        {
            "bookings": bookings,
            "has_unpaid_damage": has_unpaid_damage
        }
    )


@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if booking.status == "pending":
        booking.status = "cancelled"
        booking.save()

        Notification.objects.create(
            user=booking.user,
            message="Your booking has been cancelled."
        )

    return redirect("my_bookings")

# model
def can_user_book(user):
    unpaid_damage = DamageReport.objects.filter(
        booking__user=user,
        is_paid=False
    ).exists()
    return not unpaid_damage


def has_unpaid_damage(user):
    return DamageReport.objects.filter(
        booking__user=user,
        is_paid=False
    ).exists()


@login_required
def booking_guard(request):
    if has_unpaid_damage(request.user):
        messages.error(
            request,
            "You have unpaid damage charges. "
            "Please clear them to book vehicles."
        )
        return redirect("customer_damage_reports")


@login_required
def customer_damage_detail(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        user=request.user
    )

    report = (
        DamageReport.objects
        .filter(booking=booking)
        .order_by("-created_at")
        .first()
    )

    if not report:
        messages.error(request, "No damage report found.")
        return redirect("my_bookings")

    photos = DamagePhoto.objects.filter(report=report)  # ✅ FIX

    return render(
        request,
        "customer_damage_detail.html",
        {
            "booking": booking,
            "report": report,
            "photos": photos
        }
    )


@login_required
def pay_damage_charge(request, report_id):
    report = get_object_or_404(
        DamageReport,
        id=report_id,
        booking__user=request.user
    )

    if report.is_paid:
        messages.info(request, "Damage already paid.")
        return redirect("my_bookings")

    if request.method == "POST":
        report.is_paid = True
        report.save()

        Notification.objects.create(
            user=request.user,
            message="Damage payment successful. You may book again."
        )
        Notification.objects.create(
            user=User.objects.filter(is_superuser=True).first(),
            message=(
                f"Damage payment completed for booking #{report.booking.id} "
                f"({report.booking.vehicle.vehicle_name})"
            )
        )

        messages.success(request, "Payment completed.")
        return redirect("my_bookings")

    return render(request, "pay_damage_charge.html", {"report": report})

@login_required
def admin_dashboard(request):
    unread_count = get_unread_notification_count(request.user)
    return render(request, "admin_dashboard.html", {
        "unread_notification_count": unread_count
    })

@login_required
def admin_users(request):
    if not request.user.is_superuser:
        return redirect("home")

    users = User.objects.filter(is_superuser=False).prefetch_related("groups")

    users_with_roles = []
    for user in users:
        if user.is_superuser:
            role = "admin"
        elif user.groups.filter(name="owner").exists():
            role = "owner"
        else:
            role = "customer"

        users_with_roles.append({
            "user": user,
            "role": role
        })

    return render(request, "admin_users.html", {
        "users_with_roles": users_with_roles
    })

@login_required
def admin_add_vehicle(request):
    if not request.user.is_superuser:
        return redirect("home")

    if request.method == "POST":
        Vehicle.objects.create(
            owner=None,  # admin-added vehicle
            vehicle_name=request.POST.get("vehicle_name"),
            vehicle_type=request.POST.get("vehicle_type"),
            number_plate=request.POST.get("number_plate"),
            seats=request.POST.get("seats"),
            price_per_hour=request.POST.get("price_per_hour"),
            image=request.FILES.get("image"),
        )
        messages.success(request, "Vehicle added successfully!")
        return redirect("admin_vehicles")

    return render(request, "admin_add_vehicle.html")

@login_required
def admin_vehicles(request):
    if not request.user.is_superuser:
        return redirect("home")

    vehicles = Vehicle.objects.select_related("owner")

    q = request.GET.get("q")
    if q:
        vehicles = vehicles.filter(
            vehicle_name__icontains=q
        ) | vehicles.filter(
            number_plate__icontains=q
        )

    vehicle_type = request.GET.get("type")
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)

    return render(request, "admin_vehicles.html", {"vehicles": vehicles})


@login_required
def admin_update_vehicle(request, id):
    if not request.user.is_superuser:
        return redirect("home")

    vehicle = get_object_or_404(Vehicle, id=id)

    if request.method == "POST":
        vehicle.vehicle_name = request.POST.get("vehicle_name")
        vehicle.vehicle_type = request.POST.get("vehicle_type")
        vehicle.number_plate = request.POST.get("number_plate")
        vehicle.seats = request.POST.get("seats")
        vehicle.price_per_hour = request.POST.get("price_per_hour")

        if request.FILES.get("image"):
            vehicle.image = request.FILES.get("image")

        vehicle.save()
        messages.success(request, "Vehicle updated successfully!")
        return redirect("admin_vehicles")

    return render(request, "admin_update_vehicle.html", {"vehicle": vehicle})


@login_required
def admin_delete_vehicle(request, id):
    if not request.user.is_superuser:
        return redirect("home")

    vehicle = get_object_or_404(Vehicle, id=id)
    vehicle.delete()
    messages.success(request, "Vehicle deleted successfully!")
    return redirect("admin_vehicles")

@login_required
def admin_bookings(request):
    if not request.user.is_superuser:
        return redirect("home")
    bookings = Booking.objects.select_related("vehicle", "user").order_by("-ordered_at")
    return render(request, "admin_bookings.html", {"bookings": bookings})

@login_required
def admin_revenue(request):
    if not request.user.is_superuser:
        return redirect("home")
    total_revenue = Booking.objects.filter(
        status__in=["confirmed", "returned"]
    ).aggregate(total=models.Sum("total_price"))["total"] or 0

    return render(request, "admin_revenue.html", {
        "total_revenue": total_revenue
    })


@login_required
def admin_analytics(request):
    if not request.user.is_superuser:
        return redirect("home")

    data = {
        "total_users": User.objects.count(),
        "total_owners": User.objects.filter(groups__name="owner").count(),
        "total_vehicles": Vehicle.objects.count(),
        "total_bookings": Booking.objects.count(),
    }

    return render(request, "admin_analytics.html", data)

@login_required
def approve_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not booking.handover_photos.exists():
        messages.error(request, "Handover photos not uploaded yet.")
        return redirect("admin_bookings")
    booking.status = "confirmed"
    booking.save()
    Notification.objects.create(
        user=booking.user,
        message="Your booking has been confirmed."
    )
    return redirect("admin_bookings")


@login_required
def mark_in_use(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status != "confirmed":
        messages.error(request, "Invalid action.")
        return redirect("admin_bookings")
    booking.status = "in_use"
    booking.save()
    return redirect("admin_bookings")


@login_required
def mark_returned(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status != "in_use":
        return redirect("admin_bookings")
    booking.status = "returned"
    booking.save()
    Notification.objects.create(
        user=booking.user,
        message=f"{booking.vehicle.vehicle_name} returned successfully."
    )
    return redirect("admin_bookings")


@login_required
def admin_damage_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    report = get_object_or_404(DamageReport, booking=booking)

    if request.method == "POST":
        booking.damage_paid = False
        booking.save()

        Notification.objects.create(
            user=booking.user,
            message="Damage confirmed. Please complete payment."
        )

        return redirect("admin_bookings")

    return render(request, "admin_damage_review.html", {
        "booking": booking,
        "report": report
    })



@login_required
def admin_damage_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    damage_report = getattr(booking, "damage_report", None)
    handover_photos = VehicleHandoverPhoto.objects.filter(
        booking=booking
    )
    damage_photos = []
    if damage_report:
        damage_photos = DamagePhoto.objects.filter(
            report=damage_report
        )

    return render(
        request,
        "admin_damage_details.html",
        {
            "booking": booking,
            "damage_report": damage_report,
            "handover_photos": handover_photos,
            "damage_photos": damage_photos,
        }
    )


@login_required
def mark_damage_paid(request, damage_id):
    report = get_object_or_404(DamageReport, id=damage_id)
    report.is_paid = True
    report.save()

    messages.success(request, "Damage marked as paid.")
    return redirect("admin_damage_details", booking_id=report.booking.id)


@login_required
def admin_damage_report_list(request):
    reports = DamageReport.objects.select_related(
        "vehicle", "booking", "booking__user"
    ).order_by("-created_at")

    return render(
        request,
        "damage_report_list.html",
        {"reports": reports}
    )


@login_required
def admin_damage_report_detail(request, report_id):
    report = get_object_or_404(DamageReport, id=report_id)
    damage_photos = DamagePhoto.objects.filter(report=report)
    handover_photos = VehicleHandoverPhoto.objects.filter(
        booking=report.booking
    )

    return render(
        request,
        "damage_report_detail.html",
        {
            "report": report,
            "handover_photos": handover_photos,
            "damage_photos": damage_photos
        }
    )

@login_required
def owner_dashboard(request):
    if not request.user.groups.filter(name="owner").exists():
        return redirect("home")

    context = {
        "unread_count": get_unread_notification_count(request.user)
    }

    return render(request, "owner_dashboard.html", context)

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        vehicle = Vehicle.objects.create(
            owner=request.user,
            vehicle_name=request.POST.get("vehicle_name"),
            vehicle_type=request.POST.get("vehicle_type"),
            number_plate=request.POST.get("number_plate"),
            seats=request.POST.get("number_of_seats"),
            price_per_hour=request.POST.get("price_per_hour"),
            image=request.FILES.get("image"),
        )
        messages.success(request, "Vehicle added successfully!")
        return redirect("owner_dashboard")
    return render(request, "add_vehicle.html")

@login_required
def update_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)
    if vehicle.owner != request.user:
        messages.error(request, "You are not allowed to edit this vehicle")
        return redirect("home")
    if request.method == "POST":
        vehicle.vehicle_name = request.POST.get("vehicle_name")
        vehicle.vehicle_type = request.POST.get("vehicle_type")
        vehicle.number_plate = request.POST.get("number_plate")
        vehicle.seats = request.POST.get("number_of_seats")
        vehicle.price_per_hour = request.POST.get("price_per_hour")
        if request.FILES.get("image"):
            vehicle.image = request.FILES.get("image")
        vehicle.save()
        messages.success(request, "Vehicle updated successfully!")
        return redirect("owner_vehicle_list")
    return render(request, "update_vehicle.html", {"vehicle": vehicle})

@login_required
def delete_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)
    vehicle.delete()
    messages.success(request, "Vehicle deleted successfully!")
    return redirect("home")


@login_required
def owner_vehicles(request):
    if not request.user.groups.filter(name="owner").exists():
        messages.error(request, "Access denied")
        return redirect("home")

    vehicles = Vehicle.objects.filter(owner=request.user)

    return render(request, "owner_vehicles_list.html", {
        "vehicles": vehicles
    })

@login_required
def owner_bookings(request):
    if not request.user.groups.filter(name="owner").exists():
        messages.error(request, "Access denied")
        return redirect("home")
    bookings = (
        Booking.objects
        .filter(vehicle__owner=request.user)
        .select_related("vehicle", "user")
        .prefetch_related("handover_photos",
            Prefetch("damage_report", queryset=DamageReport.objects.all())
        )
        .order_by("-ordered_at")
    )
    return render(request,"owner_bookings.html",{"bookings": bookings})


@login_required
def upload_handover_photos(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        vehicle__owner=request.user
    )
    if booking.handover_photos.exists():
        messages.warning(request, "Handover photos already uploaded.")
        return redirect("owner_vehicle_bookings")

    if request.method == "POST":
        photos = request.FILES.getlist("photos")

        if not photos:
            messages.error(request, "Upload at least one photo.")
            return redirect(request.path)

        for photo in photos:
            VehicleHandoverPhoto.objects.create(
                booking=booking,
                image=photo
            )

        Notification.objects.create(
            user=User.objects.filter(is_superuser=True).first(),
            message=(
                f"Handover photos uploaded for booking #{booking.id} "
                f"({booking.vehicle.vehicle_name})"
            )
        )

        messages.success(request, "Handover photos uploaded successfully.")
        return redirect("owner_vehicle_bookings")

    return render(request, "upload_handover_photos.html", {"booking": booking})


@login_required
def owner_add_damage_report(request, booking_id):
    booking = get_object_or_404(
        Booking,
        id=booking_id,
        vehicle__owner=request.user
    )
    if hasattr(booking, "damage_report"):
        messages.error(request, "Damage report already exists for this booking.")
        return redirect("owner_vehicle_bookings")

    if request.method == "POST":
        description = request.POST.get("description")
        extra_charge = request.POST.get("extra_charge")
        photos = request.FILES.getlist("photos")

        if not photos:
            messages.error(request, "Upload at least one damage photo")
            return redirect(request.path)

        report = DamageReport.objects.create(
            booking=booking,
            vehicle=booking.vehicle,
            reported_by=request.user,
            description=description,
            extra_charge=extra_charge,
            is_paid=False
        )
        Notification.objects.create(
            user=User.objects.filter(is_superuser=True).first(),
            message=(
                f"Damage reported for {booking.vehicle.vehicle_name} "
                f"(Booking #{booking.id})"
            )
        )
        for photo in photos:
            DamagePhoto.objects.create(
                report=report,
                image=photo
            )
        booking.status = "damage_reported"
        booking.save()
        Notification.objects.create(
            user=booking.user,
            message=(
                f"Damage reported for {booking.vehicle.vehicle_name}. "
                f"Extra charge ₹{extra_charge}. Please pay to continue."
            )
        )

        messages.success(request, "Damage report submitted successfully")
        return redirect("owner_vehicle_bookings")
    
    return render(
        request,
        "owner_add_damage_report.html",
        {"booking": booking}
    )

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(request, "notifications.html", {
        "notifications": notifications
    })


@login_required
@require_POST
def mark_notification_read(request):
    notif_id = request.POST.get("id")
    Notification.objects.filter(
        id=notif_id,
        user=request.user
    ).update(is_read=True)
    return JsonResponse({"status": "ok"})


def get_unread_notification_count(user):
    if user.is_authenticated:
        return Notification.objects.filter(
            user=user,
            is_read=False
        ).count()
    return 0

@login_required
def unread_notification_count(request):
    count = get_unread_notification_count(request.user)
    return JsonResponse({"count": count})