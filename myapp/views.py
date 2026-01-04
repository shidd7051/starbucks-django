import traceback
import sys
import time
import random

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required

from .models import UserRegistration, OTP , Contact
from .utils import send_otp


# =====================
# HOME PAGES
# =====================

def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def registration(request):
    return render(request, "registration.html")


# =====================
# HELPER
# =====================

def _make_username(base):
    username = slugify(base)[:150] or "user"
    if not User.objects.filter(username=username).exists():
        return username
    return username + "-" + str(int(time.time()))


# =====================
# REGISTER + SEND OTP
# =====================

def register(request):
    if request.method != "POST":
        return redirect("registration")

    try:
        first = request.POST.get("first_name", "").strip()
        last = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip().lower()
        phone = request.POST.get("phone", "").strip()
        p1 = request.POST.get("password1", "")
        p2 = request.POST.get("password2", "")
        receive = True if request.POST.get("receive_emails") == "on" else False

        if not all([first, last, email, phone, p1, p2]):
            messages.error(request, "All fields are required.")
            return redirect("registration")

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect("registration")

        if p1 != p2:
            messages.error(request, "Passwords do not match.")
            return redirect("registration")

        username = _make_username(email.split("@")[0])

        user = User.objects.create_user(
            username=username,
            email=email,
            password=p1,
            first_name=first,
            last_name=last,
            is_active=False   # 🔐 OTP REQUIRED
        )

        UserRegistration.objects.create(
            user=user,
            full_name=f"{first} {last}",
            email=email,
            receive_emails=receive
        )

        otp_code = str(random.randint(100000, 999999))

        OTP.objects.create(
            user=user,
            phone=phone,
            code=otp_code
        )

        send_otp(phone, otp_code)

        request.session["otp_user_id"] = user.id

        messages.success(request, "OTP sent to your phone number.")
        return redirect("verify_otp")

    except Exception as exc:
        print("Register error:", exc, file=sys.stderr)
        traceback.print_exc()
        messages.error(request, "Registration failed.")
        return redirect("registration")


# =====================
# VERIFY OTP
# =====================

def verify_otp(request):
    if request.method == "POST":
        code = request.POST.get("otp")
        user_id = request.session.get("otp_user_id")

        try:
            otp = OTP.objects.get(user_id=user_id, code=code)

            user = otp.user
            user.is_active = True
            user.save()

            otp.delete()
            del request.session["otp_user_id"]

            messages.success(request, "Account verified successfully. Please login.")
            return redirect("login")

        except OTP.DoesNotExist:
            messages.error(request, "Invalid OTP.")

    return render(request, "verify_otp.html")


# =====================
# SEND / RESEND OTP
# =====================

def send_otp_view(request):
    user_id = request.session.get("otp_user_id")

    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("registration")

    try:
        otp_obj = OTP.objects.get(user_id=user_id)

        new_otp = str(random.randint(100000, 999999))
        otp_obj.code = new_otp
        otp_obj.save()

        send_otp(otp_obj.phone, new_otp)

        messages.success(request, "OTP resent successfully.")
        return redirect("verify_otp")

    except OTP.DoesNotExist:
        messages.error(request, "OTP not found. Please register again.")
        return redirect("registration")


# =====================
# LOGIN
# =====================

def login_view(request):
    if request.method == "POST":
        try:
            email = request.POST.get("email", "").strip().lower()
            password = request.POST.get("password", "")

            if not email or not password:
                messages.error(request, "Email and password required.")
                return render(request, "login.html", {"email": email})

            reg = UserRegistration.objects.get(email=email)
            user = authenticate(
                request,
                username=reg.user.username,
                password=password
            )

            if user and user.is_active:
                auth_login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect("dashboard")

            messages.error(request, "Invalid credentials or account not verified.")
            return render(request, "login.html", {"email": email})

        except UserRegistration.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "login.html", {"email": email})

        except Exception as exc:
            print("Login error:", exc, file=sys.stderr)
            traceback.print_exc()
            messages.error(request, "Unexpected login error.")
            return render(request, "login.html")

    return render(request, "login.html")


# =====================
# LOGOUT
# =====================

def logout_view(request):
    auth_logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect("index")


# =====================
# DASHBOARD
# =====================

@login_required(login_url="login")
def dashboard(request):
    reg = UserRegistration.objects.filter(user=request.user).first()
    return render(request, "dashboard.html", {"reg": reg})






# Contact views ----------------

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        Contact.objects.create(
            name=name,
            email=email,
            message=message
        )

        # SUCCESS MESSAGE
        messages.success(request, "Your form is successfully submitted ✔")

        return redirect('contact')  # reload page to show message

    return render(request, 'contact.html')