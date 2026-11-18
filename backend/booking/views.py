from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import User, Hotel, Room, Booking, Review, Payment
from .serializers import UserSerializer, HotelSerializer, RoomSerializer, BookingSerializer, ReviewSerializer, PaymentSerializer
from .permissions import is_admin

@api_view(["POST"])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    return Response({"message": "Account created. You can now log in.", "user_id": user.id}, status=status.HTTP_201_CREATED)

class HotelViewSet(viewsets.ModelViewSet):
    serializer_class = HotelSerializer
    def get_queryset(self):
        user = self.request.user
        qs = Hotel.objects.all()
        if not user.is_authenticated:
            qs = qs.filter(is_approved=True)
        elif not is_admin(user) and user.role != "owner":
            qs = qs.filter(is_approved=True)
        elif user.role == "owner" and not is_admin(user):
            qs = qs.filter(owner=user)
        city = self.request.query_params.get("city")
        if city:
            qs = qs.filter(city__icontains=city)
        max_price = self.request.query_params.get("max_price")
        if max_price:
            qs = qs.filter(rooms__price_per_night__lte=max_price).distinct()
        return qs
    def perform_create(self, serializer):
        if self.request.user.role != "owner" and not is_admin(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only hotel owners can create hotels.")
        serializer.save()
    def perform_update(self, serializer):
        obj = self.get_object()
        if not is_admin(self.request.user) and obj.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own hotels.")
        serializer.save()
    def perform_destroy(self, instance):
        if not is_admin(self.request.user) and instance.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own hotels.")
        instance.delete()

class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    def get_queryset(self):
        qs = Room.objects.select_related("hotel")
        hotel_id = self.request.query_params.get("hotel")
        if hotel_id:
            qs = qs.filter(hotel_id=hotel_id)
        if not self.request.user.is_authenticated or (self.request.user.role == "customer" and not is_admin(self.request.user)):
            qs = qs.filter(hotel__is_approved=True, is_available=True)
        elif self.request.user.role == "owner" and not is_admin(self.request.user):
            qs = qs.filter(hotel__owner=self.request.user)
        return qs
    def perform_create(self, serializer):
        user = self.request.user
        hotel = serializer.validated_data["hotel"]
        if not is_admin(user) and (user.role != "owner" or hotel.owner != user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the hotel's owner can add rooms.")
        serializer.save()

class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]
    def get_queryset(self):
        user = self.request.user
        qs = Booking.objects.select_related("room__hotel", "customer")
        if is_admin(user):
            return qs
        if user.role == "owner":
            return qs.filter(room__hotel__owner=user)
        return qs.filter(customer=user)
    def perform_create(self, serializer):
        if self.request.user.role != "customer":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only customers can book rooms.")
        room = serializer.validated_data["room"]
        if not room.hotel.is_approved:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("This hotel is not approved yet.")
        serializer.save()
    def perform_update(self, serializer):
        booking = self.get_object()
        user = self.request.user
        if user.role == "owner" and booking.room.hotel.owner == user:
            new_status = self.request.data.get("status")
            if new_status not in ["confirmed", "cancelled"]:
                from rest_framework.exceptions import ValidationError
                raise ValidationError("Owners may set status to confirmed or cancelled.")
            serializer.save(status=new_status)
        elif booking.customer == user and self.request.data.get("status") == "cancelled":
            serializer.save(status="cancelled")
        elif is_admin(user):
            serializer.save()
        else:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You cannot update this booking.")
    def perform_destroy(self, instance):
        if not is_admin(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only admins can delete bookings.")
        instance.delete()

class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    def get_queryset(self):
        qs = Review.objects.select_related("customer", "hotel")
        hotel_id = self.request.query_params.get("hotel")
        if hotel_id:
            qs = qs.filter(hotel_id=hotel_id)
        return qs
    def perform_create(self, serializer):
        if self.request.user.role != "customer":
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only customers can review hotels.")
        hotel = serializer.validated_data["hotel"]
        stayed = Booking.objects.filter(customer=self.request.user, room__hotel=hotel, status="confirmed", check_out__lte=timezone.localdate()).exists()
        if not stayed:
            from rest_framework.exceptions import ValidationError
            raise ValidationError("You can review after a confirmed stay has ended.")
        serializer.save()
    def perform_destroy(self, instance):
        if not is_admin(self.request.user) and instance.customer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You cannot delete this review.")
        instance.delete()

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    http_method_names = ["get", "post", "head", "options"]
    def get_queryset(self):
        user = self.request.user
        qs = Payment.objects.select_related("booking__room__hotel", "booking__customer")
        if is_admin(user):
            return qs
        if user.role == "owner":
            return qs.filter(booking__room__hotel__owner=user)
        return qs.filter(booking__customer=user)
    def create(self, request, *args, **kwargs):
        booking_id = request.data.get("booking")
        method = request.data.get("method")
        fail = str(request.data.get("simulate_failure", "false")).lower() == "true"
        if method not in ["card", "upi", "cash"]:
            return Response({"method": "Choose card, upi or cash."}, status=400)
        booking = get_object_or_404(Booking, pk=booking_id)
        if booking.customer_id != request.user.id and not is_admin(request.user):
            return Response({"detail": "You can only pay for your own booking."}, status=403)
        if booking.status == "cancelled":
            return Response({"detail": "Cancelled bookings cannot be paid."}, status=400)
        if hasattr(booking, "payment"):
            return Response(PaymentSerializer(booking.payment).data, status=200)
        payment = Payment.objects.create(
            booking=booking, amount=booking.total_price, method=method,
            status="failed" if fail else "success",
            paid_date=None if fail else timezone.now()
        )
        if not fail:
            booking.status = "confirmed"
            booking.save(update_fields=["status"])
        return Response(PaymentSerializer(payment).data, status=201)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def admin_users(request):
    if not is_admin(request.user):
        return Response({"detail": "Admin access required."}, status=403)
    users = User.objects.all().order_by("id")
    return Response(UserSerializer(users, many=True).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def admin_approve_hotel(request, pk):
    if not is_admin(request.user):
        return Response({"detail": "Admin access required."}, status=403)
    hotel = get_object_or_404(Hotel, pk=pk)
    hotel.is_approved = bool(request.data.get("is_approved", True))
    hotel.save(update_fields=["is_approved"])
    return Response(HotelSerializer(hotel).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    return Response(UserSerializer(request.user).data)
