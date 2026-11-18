from datetime import date
from rest_framework import serializers
from .models import User, Hotel, Room, Booking, Review, Payment

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "phone"]
        read_only_fields = ["id"]
    def create(self, validated_data):
        password = validated_data.pop("password")
        role = validated_data.pop("role", "customer")
        if role == "admin":
            role = "customer"
        user = User(**validated_data, role=role)
        user.set_password(password)
        user.save()
        return user

class HotelSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.username", read_only=True)
    class Meta:
        model = Hotel
        fields = ["id", "owner", "owner_name", "name", "city", "address", "description", "image", "is_approved"]
        read_only_fields = ["owner", "is_approved"]
    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

class RoomSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source="hotel.name", read_only=True)
    class Meta:
        model = Room
        fields = ["id", "hotel", "hotel_name", "room_type", "price_per_night", "capacity", "is_available"]
    def validate(self, attrs):
        hotel = attrs.get("hotel", getattr(self.instance, "hotel", None))
        request = self.context.get("request")
        if request and not (request.user.is_staff or request.user.role == "admin") and hotel and hotel.owner != request.user:
            raise serializers.ValidationError("You can only manage rooms for your own hotels.")
        return attrs

class BookingSerializer(serializers.ModelSerializer):
    hotel_name = serializers.CharField(source="room.hotel.name", read_only=True)
    room_type = serializers.CharField(source="room.room_type", read_only=True)
    class Meta:
        model = Booking
        fields = ["id", "customer", "room", "hotel_name", "room_type", "check_in", "check_out", "total_price", "status", "created_at"]
        read_only_fields = ["customer", "total_price", "status", "created_at"]
    def validate(self, attrs):
        check_in = attrs.get("check_in")
        check_out = attrs.get("check_out")
        room = attrs.get("room")
        if check_in and check_in < date.today():
            raise serializers.ValidationError("Check-in cannot be in the past.")
        if check_in and check_out and check_out <= check_in:
            raise serializers.ValidationError("Check-out must be after check-in.")
        if room and not room.is_available:
            raise serializers.ValidationError("This room is not currently available.")
        if room and check_in and check_out:
            conflicts = Booking.objects.filter(room=room, status__in=["pending", "confirmed"], check_in__lt=check_out, check_out__gt=check_in)
            if self.instance:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            if conflicts.exists():
                raise serializers.ValidationError("This room is already booked for some of those dates.")
        return attrs
    def create(self, validated_data):
        room = validated_data["room"]
        nights = (validated_data["check_out"] - validated_data["check_in"]).days
        validated_data["total_price"] = room.price_per_night * nights
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.username", read_only=True)
    class Meta:
        model = Review
        fields = ["id", "customer", "customer_name", "hotel", "rating", "comment", "created_at"]
        read_only_fields = ["customer", "created_at"]
    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value
    def create(self, validated_data):
        validated_data["customer"] = self.context["request"].user
        return super().create(validated_data)

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "booking", "amount", "method", "status", "transaction_id", "paid_date"]
        read_only_fields = ["amount", "status", "transaction_id", "paid_date"]
