from rest_framework.permissions import BasePermission, SAFE_METHODS

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser or user.role == "admin")

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return is_admin(request.user)

class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_admin(request.user):
            return True
        owner = getattr(obj, "owner", None)
        if owner is None and hasattr(obj, "hotel"):
            owner = obj.hotel.owner
        return owner == request.user

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "customer"
