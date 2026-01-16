import requests

# ================= VERIFY PAYSTACK =================
def verify_paystack_payment(reference):
    PAYSTACK_SECRET_KEY = "sk_test_adb8f6fbc4bab87dc6814514ab1d7b9df87faea4"
    url = f"https://api.paystack.co/transaction/verify/{reference}"

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(url, headers=headers)
    return response.json()