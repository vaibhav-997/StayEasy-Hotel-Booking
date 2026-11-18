from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import register, HotelViewSet, RoomViewSet, BookingViewSet, ReviewViewSet, PaymentViewSet, admin_users, admin_approve_hotel, current_user

router = DefaultRouter()
router.register("hotels", HotelViewSet, basename="hotel")
router.register("rooms", RoomViewSet, basename="room")
router.register("bookings", BookingViewSet, basename="booking")
router.register("reviews", ReviewViewSet, basename="review")
router.register("payments", PaymentViewSet, basename="payment")

urlpatterns = [
    path("auth/register/", register),
    path("auth/me/", current_user),
    path("admin/users/", admin_users),
    path("admin/hotels/<int:pk>/approve/", admin_approve_hotel),
    path("", include(router.urls)),
]
