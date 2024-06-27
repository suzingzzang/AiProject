from django.conf import settings
from twilio.rest import Client


def send_verification_sms(phone_number, verification_code):
    Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    # message = client.messages.create(body=f"Your verification code is {verification_code}", from_=settings.TWILIO_PHONE_NUMBER, to=phone_number)
