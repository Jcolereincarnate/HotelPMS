from django.core.mail import send_mail
from hotel_pms import settings as SETTINGS

def send_notification(subject, message,receiver):
    send_mail(
        subject=subject ,
        message=message,
        from_email=SETTINGS.DEFAULT_FROM_EMAIL,   
        recipient_list=[receiver],
        fail_silently=False,
    )