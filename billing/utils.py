import requests
from django.conf import settings
import secrets
from django.db.models import Sum, Q

class PaystackAPI:
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.public_key = settings.PAYSTACK_PUBLIC_KEY
    
    def initialize_transaction(self, email, amount, reference, callback_url):
        url = f"{self.BASE_URL}/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        data = {
            "email": email,
            "amount": int(amount * 100), 
            "reference": reference,
            "callback_url": callback_url
        }
        
        response = requests.post(url, json=data, headers=headers)
        return response.json()
    
    def verify_transaction(self, reference):
        url = f"{self.BASE_URL}/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {self.secret_key}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


def generate_payment_reference():
    return f"PAY-{secrets.token_urlsafe(16)}"



def update_folio_totals(folio):
    unpaid_items_total = folio.line_items.filter(status='unpaid').aggregate(
        total=Sum('total')
    )['total'] or 0
    total_charges = unpaid_items_total + folio.service_charges + folio.taxes - folio.discount
    folio.balance += total_charges
    folio.total_amount = folio.room_charges + folio.service_charges + folio.taxes - folio.discount

    folio.save()
