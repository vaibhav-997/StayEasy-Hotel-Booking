from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Hotel, Room, Booking, Review, Payment

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("StayEasy details", {"fields": ("role", "phone")}),)
    list_display = ("username", "email", "role", "is_staff", "is_active")

admin.site.register(Hotel)
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Review)
admin.site.register(Payment)
