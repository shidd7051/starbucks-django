from django.contrib import admin
from .models import UserRegistration, OTP, Contact


# -------------------------------
# USER REGISTRATION ADMIN
# -------------------------------
@admin.register(UserRegistration)
class UserRegistrationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "created_at")
    search_fields = ("full_name", "email")
    list_filter = ("created_at",)


# -------------------------------
# OTP ADMIN
# -------------------------------
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "phone", "code", "created_at")
    search_fields = ("user__email", "phone")
    list_filter = ("created_at",)


# -------------------------------
# CONTACT ADMIN
# -------------------------------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")
    list_filter = ("created_at",)
