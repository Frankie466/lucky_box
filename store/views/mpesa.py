import base64
import json
import logging
import requests
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from requests.auth import HTTPBasicAuth
from django.utils.timezone import now

# Import RewardPayment model
from store.models.reward import RewardPayment  

logger = logging.getLogger(__name__)

# 1. Generate M-Pesa Access Token
def generate_mpesa_token():
    """Generate M-Pesa API access token."""
    url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get('access_token')
        if access_token:
            return access_token
    return None

# 2. Format Phone Number for M-Pesa
def format_phone_number(phone_number):
    """Ensure phone number is in the correct format for M-Pesa (without leading zero)."""
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]  # Convert 07XX... to 2547XX...
    return phone_number

# 3. Generate M-Pesa Password
def generate_password(shortcode, passkey):
    """Generate password using shortcode, passkey, and timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = f"{shortcode}{passkey}{timestamp}"
    return base64.b64encode(password_str.encode()).decode()

# 4. Initiate STK Push Payment
def initiate_mpesa_payment(phone_number, amount, callback_url):
    """Initiate M-Pesa STK push payment."""
    token = generate_mpesa_token()
    if not token:
        return {"error": "Failed to generate token"}

    phone_number = format_phone_number(phone_number)

    url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": f"Bearer {token}"}

    payload = {
        "BusinessShortCode": settings.BUSINESS_SHORTCODE,
        "Password": generate_password(settings.BUSINESS_SHORTCODE, settings.MPESA_PASSKEY),
        "Timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
        "TransactionType": "CustomerBuyGoodsOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": "4976566",  # Your M-Pesa shortcode
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": "Lucky Box",
        "TransactionDesc": "Payment for lucky box"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return {"message": "Payment initiated! Please complete the transaction to see your reward."}
    return {"error": f"Payment initiation failed: {response.text}"}

# 5. Handle M-Pesa Callback Response
@csrf_exempt
def mpesa_callback_view(request):
    """Handle the M-Pesa callback response and update the reward system."""
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            logger.info(f"Callback data received: {callback_data}")

            result_code = callback_data.get('ResultCode')
            result_description = callback_data.get('ResultDesc', 'No description provided')
            merchant_request_id = callback_data.get("MerchantRequestID", "")
            checkout_request_id = callback_data.get("CheckoutRequestID", "")
            phone_number = callback_data.get("PhoneNumber", "")
            amount = callback_data.get("Amount", 0)

            # Log the ResultCode and ResultDescription for debugging
            logger.info(f"Payment Status: {result_description} (ResultCode: {result_code})")

            if result_code == 0:  # Success
                reward_payment = RewardPayment.objects.filter(
                    phone_number=phone_number, is_successful=False
                ).first()

                if reward_payment:
                    # Update the reward record
                    reward_payment.is_successful = True
                    reward_payment.transaction_id = checkout_request_id
                    reward_payment.date = now()
                    reward_payment.reward = "Lucky Box Reward"  # Customize as needed
                    reward_payment.save()
                    logger.info(f"Reward payment updated for phone number {phone_number}")
                else:
                    # Create a new reward entry
                    reward_payment = RewardPayment.objects.create(
                        phone_number=phone_number,
                        amount=amount,
                        transaction_id=checkout_request_id,
                        is_successful=True,
                        reward="Lucky Box Reward",
                        date=now()
                    )
                    logger.info(f"New reward payment created for phone number {phone_number}")

                # Return the response including the reward information
                return JsonResponse({
                    "status": "Payment processed successfully!",
                    "reward": reward_payment.reward  # Include the reward key
                })

            else:
                # Handle failed payments
                logger.error(f"Payment failed for checkout ID {checkout_request_id} with error: {result_description}")
                return JsonResponse({"error": f"Payment failed: {result_description}"}, status=400)

        except Exception as e:
            logger.error(f"Error processing callback: {str(e)}")
            return JsonResponse({"error": "Invalid callback data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)

# 6. Trigger M-Pesa STK Push
@csrf_exempt
def mpesa_callback_view(request):
    """Handle the M-Pesa callback response and update the reward system."""
    if request.method == 'POST':
        try:
            callback_data = json.loads(request.body)
            logger.info(f"Callback data received: {json.dumps(callback_data, indent=4)}")  # Log the response

            # Extract core response details
            body = callback_data.get("Body", {})
            stk_callback = body.get("stkCallback", {})
            result_code = stk_callback.get("ResultCode")
            result_description = stk_callback.get("ResultDesc", "No description provided")
            merchant_request_id = stk_callback.get("MerchantRequestID", "")
            checkout_request_id = stk_callback.get("CheckoutRequestID", "")
            
            # Extract CallbackMetadata items
            callback_metadata = stk_callback.get("CallbackMetadata", {}).get("Item", [])
            phone_number = ""
            amount = 0
            transaction_id = ""

            for item in callback_metadata:
                if item["Name"] == "MpesaReceiptNumber":
                    transaction_id = item["Value"]
                elif item["Name"] == "PhoneNumber":
                    phone_number = str(item["Value"])
                elif item["Name"] == "Amount":
                    amount = float(item["Value"])

            # Log extracted details
            logger.info(f"Extracted Data - Result Code: {result_code}, Amount: {amount}, Phone: {phone_number}, Txn ID: {transaction_id}")

            if result_code == 0:  # Success
                reward_payment = RewardPayment.objects.filter(
                    phone_number=phone_number, is_successful=False
                ).first()

                if reward_payment:
                    # Update the reward record
                    reward_payment.is_successful = True
                    reward_payment.transaction_id = transaction_id
                    reward_payment.date = now()
                    reward_payment.reward = "Lucky Box Reward"  # Customize as needed
                    reward_payment.save()
                    logger.info(f"Reward payment updated for phone number {phone_number}")
                else:
                    # Create a new reward entry
                    reward_payment = RewardPayment.objects.create(
                        phone_number=phone_number,
                        amount=amount,
                        transaction_id=transaction_id,
                        is_successful=True,
                        reward="Lucky Box Reward",
                        date=now()
                    )
                    logger.info(f"New reward payment created for phone number {phone_number}")

                # Return response
                return JsonResponse({
                    "status": "Payment processed successfully!",
                    "reward": reward_payment.reward
                })

            else:
                logger.error(f"Payment failed for checkout ID {checkout_request_id} with error: {result_description}")
                return JsonResponse({"error": f"Payment failed: {result_description}"}, status=400)

        except Exception as e:
            logger.error(f"Error processing callback: {str(e)}")
            return JsonResponse({"error": "Invalid callback data"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=400)
