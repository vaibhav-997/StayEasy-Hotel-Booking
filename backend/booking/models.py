import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = [("admin", "Admin"), ("owner", "Hotel owner"), ("customer", "Customer")]
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")
    phone = models.CharField(max_length=25, blank=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = "admin"
        super().save(*args, **kwargs)

class Hotel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="hotels")
    name = models.CharField(max_length=140)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.URLField(blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} — {self.city}"

class Room(models.Model):
    ROOM_TYPES = [("single", "Single"), ("double", "Double"), ("suite", "Suite")]
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.PositiveSmallIntegerField(default=2)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.hotel.name} / {self.room_type}"

class Booking(models.Model):
    STATUSES = [("pending", "Pending"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled")]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    room = models.ForeignKey(Room, on_delete=models.PROTECT, related_name="bookings")
    check_in = models.DateField()
    check_out = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=12, choices=STATUSES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking #{self.pk} — {self.status}"

class Review(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hotel.name}: {self.rating}/5"

class Payment(models.Model):
    METHODS = [("card", "Card (demo)"), ("upi", "UPI (demo)"), ("cash", "Cash (demo)")]
    STATUSES = [("pending", "Pending"), ("success", "Success"), ("failed", "Failed"), ("refunded", "Refunded")]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=METHODS)
    status = models.CharField(max_length=10, choices=STATUSES, default="pending")
    transaction_id = models.CharField(max_length=40, unique=True, blank=True)
    paid_date = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = "DEMO-" + uuid.uuid4().hex[:12].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_id} — {self.status}"
