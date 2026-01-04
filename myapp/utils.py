from twilio.rest import Client
from django.conf import settings

def send_otp(phone, otp):
    # 🔹 LOCAL / NO TWILIO MODE
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        print("===================================")
        print("LOCAL MODE - OTP SMS NOT SENT")
        print("PHONE:", phone)
        print("OTP:", otp)
        print("===================================")
        return True   # ⭐ VERY IMPORTANT

    try:
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        client.messages.create(
            body=f"Your OTP is {otp} from Starbucks Website",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=phone
        )
        return True

    except Exception as e:
        print("Twilio error:", e)
        return False

