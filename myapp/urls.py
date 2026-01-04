from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("about/", views.about, name="about"),

    path("registration/", views.registration, name="registration"),
    path("register/", views.register, name="register"),

    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),

    path("verify-otp/", views.verify_otp, name="verify_otp"),
    path("send-otp/", views.send_otp_view, name="send_otp"),   # ✅ NEW 
     path('contact/', views.contact, name='contact'),
]
