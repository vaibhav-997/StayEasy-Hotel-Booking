
import os
import django
from datetime import date
from decimal import Decimal

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from booking.models import User, Hotel, Room, Booking, Review, Payment

# 1. Create demo users
def make_user(username, email, role, password):
    user, created = User.objects.get_or_create(
        username=username,
        defaults={"email": email, "role": role}
    )
    if created:
        user.email = email
        user.role = role
        user.set_password(password)
        user.save()
    return user

admin = User.objects.filter(username="admin_demo").first()
if not admin:
    admin = User.objects.create_superuser(
        username="admin_demo",
        email="admin@example.com",
        password="AdminDemo123!"
    )

owner1 = make_user(
    "owner_demo", "owner@example.com", "owner", "OwnerDemo123!"
)
owner2 = make_user(
    "owner2_demo", "owner2@example.com", "owner", "OwnerDemo123!"
)

customer1 = make_user(
    "customer_demo", "customer@example.com", "customer", "Customer123!"
)
customer2 = make_user(
    "customer2_demo", "customer2@example.com", "customer", "Customer123!"
)
customer3 = make_user(
    "customer3_demo", "customer3@example.com", "customer", "Customer123!"
)

print("Users ready.")

# 2. Create hotels
hotel_data = [
    (owner1, "Ocean Pearl Resort", "Goa",
     "Calangute Beach Road, Goa",
     "A relaxing beach resort with tropical views.",
     "https://images.unsplash.com/photo-1566073771259-6a8506099945",
     True),
    (owner1, "Royal Orchid Stay", "Pune",
     "Baner Road, Pune",
     "A modern city hotel for business and leisure.",
     "https://images.unsplash.com/photo-1542314831-068cd1dbfeeb",
     True),
    (owner1, "Mountain Mist Retreat", "Manali",
     "Old Manali Road, Himachal Pradesh",
     "A peaceful mountain retreat with scenic views.",
     "https://images.unsplash.com/photo-1518780664697-55e3ad937233",
     True),
    (owner2, "City Lights Hotel", "Mumbai",
     "Andheri West, Mumbai",
     "A comfortable stay close to city attractions.",
     "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa",
     True),
    (owner2, "Lakeview Residency", "Udaipur",
     "Lake Pichola Road, Udaipur",
     "A charming stay near beautiful lake views.",
     "https://images.unsplash.com/photo-1571896349842-33c89424de2d",
     False),
]

hotels = {}
for owner, name, city, address, description, image, approved in hotel_data:
    hotel = Hotel.objects.filter(name=name, owner=owner).first()
    if not hotel:
        hotel = Hotel.objects.create(
            owner=owner,
            name=name,
            city=city,
            address=address,
            description=description,
            image=image,
            is_approved=approved
        )
    hotels[name] = hotel

print("Hotels ready.")

# 3. Create two rooms per hotel
room_specs = [
    ("single", 1800, 1),
    ("double", 3000, 2),
]

rooms = {}
for hotel_name, hotel in hotels.items():
    for room_type, price, capacity in room_specs:
        room = Room.objects.filter(
            hotel=hotel, room_type=room_type
        ).first()
        if not room:
            room = Room.objects.create(
                hotel=hotel,
                room_type=room_type,
                price_per_night=Decimal(price),
                capacity=capacity,
                is_available=True
            )
        rooms[(hotel_name, room_type)] = room

print("Rooms ready.")

# 4. Create sample bookings
booking_specs = [
    (customer1, "Ocean Pearl Resort", "double",
     date(2026, 11, 10), date(2026, 11, 12), "confirmed"),
    (customer2, "Royal Orchid Stay", "single",
     date(2026, 12, 5), date(2026, 12, 7), "pending"),
    (customer3, "City Lights Hotel", "double",
     date(2026, 12, 15), date(2026, 12, 17), "confirmed"),
]

bookings = {}
for customer, hotel_name, room_type, check_in, check_out, booking_status in booking_specs:
    room = rooms[(hotel_name, room_type)]
    nights = (check_out - check_in).days
    total = room.price_per_night * nights

    booking = Booking.objects.filter(
        customer=customer,
        room=room,
        check_in=check_in,
        check_out=check_out
    ).first()

    if not booking:
        booking = Booking.objects.create(
            customer=customer,
            room=room,
            check_in=check_in,
            check_out=check_out,
            total_price=total,
            status=booking_status
        )
    bookings[hotel_name] = booking

print("Bookings ready.")

# 5. Create sample reviews
review_data = [
    (customer1, "Ocean Pearl Resort", 5,
     "Beautiful location and friendly staff."),
    (customer2, "Royal Orchid Stay", 4,
     "Clean rooms and convenient location."),
    (customer3, "City Lights Hotel", 5,
     "Comfortable stay and helpful service."),
]

for customer, hotel_name, rating, comment in review_data:
    Review.objects.get_or_create(
        customer=customer,
        hotel=hotels[hotel_name],
        defaults={"rating": rating, "comment": comment}
    )

print("Reviews ready.")

# 6. Create demo payments
payment_data = [
    ("Ocean Pearl Resort", "upi", "success"),
    ("Royal Orchid Stay", "card", "failed"),
    ("City Lights Hotel", "cash", "success"),
]

for hotel_name, method, payment_status in payment_data:
    booking = bookings[hotel_name]
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={
            "amount": booking.total_price,
            "method": method,
            "status": payment_status,
            "paid_date": (
                django.utils.timezone.now()
                if payment_status == "success" else None
            )
        }
    )
    if created and payment_status == "success":
        booking.status = "confirmed"
        booking.save(update_fields=["status"])

print("\nSUCCESS! Demo data is ready.")
print("Admin: admin_demo / AdminDemo123!")
print("Owner: owner_demo / OwnerDemo123!")
print("Customer: customer_demo / Customer123!")
print("Open http://127.0.0.1:8000/admin/")
