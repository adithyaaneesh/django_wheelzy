from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .models import Vehicle, Booking, DamageReport, UserProfile
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.decorators import login_required


from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.contrib.auth import login
from django.contrib import messages
from .models import UserProfile


def register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")
        role = request.POST.get("role")
        phone = request.POST.get("phone")
        address = request.POST.get("address")

        if not all([username, email, password, cpassword, phone, address]):
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
            address=address
        )

        if role == "owner":
            owner_group, _ = Group.objects.get_or_create(name="owner")
            user.groups.add(owner_group)

        login(request, user)
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

        if selected_role == "admin":
            if not user.is_superuser:
                messages.error(request, "You are not an admin")
                return redirect("login")

            login(request, user)
            return redirect("admin_dashboard")

        if selected_role == "owner":
            if not user.groups.filter(name="owner").exists():
                messages.error(request, "You are not registered as an owner")
                return redirect("login")

            login(request, user)
            return redirect("owner_dashboard")

        if selected_role == "customer":
            if user.is_superuser or user.groups.filter(name="owner").exists():
                messages.error(request, "Please login using the correct role")
                return redirect("login")

            login(request, user)
            return redirect("home")

        messages.error(request, "Invalid role selected")
        return redirect("login")

    return render(request, "login.html")


def logout_view(request):
    logout(request)
    return redirect("login")

def owner_dashboard(request):
    if not request.user.groups.filter(name="owner").exists():
        return redirect("home")
    return render(request, "owner_dashboard.html")

def admin_dashboard(request):
    return render(request, "admin_dashboard.html")

def home(request):
    vehicles = Vehicle.objects.all()

    active_bookings = Booking.objects.filter(
        status__in=["pending", "confirmed", "in_use"]
    ).values_list("vehicle_id", flat=True)

    return render(request, "home.html", {
        "vehicles": vehicles,
        "booked_vehicle_ids": active_bookings
    })

def all_vehicle(request):
    vehicles = Vehicle.objects.all()

    search_query = request.GET.get("q")
    vehicle_type = request.GET.get("type")
    seats = request.GET.get("seats")
    available = request.GET.get("available")

    # 🔍 Search
    if search_query:
        vehicles = vehicles.filter(vehicle_name__icontains=search_query) | \
                   vehicles.filter(number_plate__icontains=search_query)

    # 🚗 Filter by type
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)

    # 💺 Filter by seats
    if seats:
        vehicles = vehicles.filter(seats=seats)

    # 🚫 ACTIVE BOOKINGS
    booked_vehicle_ids = Booking.objects.filter(
        status__in=["pending", "confirmed", "in_use"]
    ).values_list("vehicle_id", flat=True)

    # ✅ Available only → EXCLUDE booked vehicles
    if available == "1":
        vehicles = vehicles.exclude(id__in=booked_vehicle_ids)

    return render(request, "vehicle_list.html", {
        "vehicles": vehicles,
        "booked_vehicle_ids": booked_vehicle_ids
    })

# view a vehicle details for user
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


# book a vehicle by user

def book_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == 'POST':
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)

        # 🔒 CHECK BEFORE CREATING
        existing_booking = Booking.objects.filter(
            vehicle=vehicle,
            status__in=["pending", "confirmed", "in_use"]
        ).exists()

        if existing_booking:
            messages.error(request, "This vehicle is already booked")
            return redirect("vehicle_details", vehicle.id)

        # ✅ CREATE BOOKING
        Booking.objects.create(
            user=request.user,
            vehicle=vehicle,
            start_time=start,
            end_time=end,
            status="pending"
        )

        messages.success(request, "Booking created! Proceed to payment.")
        return redirect("home")

    return render(request, "booking_form.html", {"vehicle": vehicle})


# list all bookings
# def my_booking(request):
#     bookings = Booking.objects.filter(user=request.user)
#     return render(request, "my_bookings.html", {"bookings": bookings})

def my_booking(request):
    bookings = Booking.objects.all()
    return render(request, "my_bookings.html", {"bookings": bookings})



# return a vehicle
def return_vehicle(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.method == "POST":
        damage_cost = float(request.POST.get("damage_cost", 0))
        damage_desc = request.POST.get("damage_desc", "")

        booking.status = "returned"
        booking.save()

        DamageReport.objects.create(
            booking=booking,
            damage_cost=damage_cost,
            damage_description=damage_desc
        )

        messages.info(
            request,
            f"Return processed. Refund = {booking.security_deposit - damage_cost} INR"
        )

        return redirect("my_bookings")

    return render(request, "return_vehicle.html", {"booking": booking})

# admin/owner view damage details
def damage_details(request, booking_id):
    report = get_object_or_404(DamageReport, booking_id=booking_id)
    return render(request, "damage_details.html", {"report": report})

# add vehicles by owners
def add_vehicle(request):
    if request.method == 'POST':
        vehicleName = request.POST.get("vehicle_name")
        vehicleType = request.POST.get("vehicle_type")
        number_plate = request.POST.get("number_plate")
        num_of_seats = request.POST.get("number_of_seats")
        price_per_hour = request.POST.get("price_per_hour")
        image = request.FILES.get("image")

        vehicle = Vehicle.objects.create(
            vehicle_name=vehicleName,
            vehicle_type=vehicleType,
            number_plate=number_plate,
            seats=num_of_seats,
            price_per_hour=price_per_hour,
            image=image,
        )

        messages.success(request, "Vehicle added successfully!!")
        return redirect('home')

    return render(request, "add_vehicle.html")

# delete a vehicle 
def delete_vehicle(request, id):
    vehicle = get_object_or_404(Vehicle, id=id)
    vehicle.delete()
    messages.success(request, "Vehicle deleted successfully!")
    return redirect("home")