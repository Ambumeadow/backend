import requests
import os

# ================= VERIFY PAYSTACK =================
def verify_paystack_payment(reference):
    PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY")
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    return response.json()