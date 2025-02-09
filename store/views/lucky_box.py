import random
import logging
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from store.models.payment import Payment
from store.models.reward import RewardPayment  # Ensure this model exists
from store.views.mpesa import initiate_mpesa_payment

logger = logging.getLogger(__name__)

def validate_phone_number(phone_number):
    """Validates Safaricom phone number format (07xxxxxxxx)."""
    return re.fullmatch(r"^07\d{8}$", phone_number)

@login_required
def lucky_box(request):
    """Handles the lucky box request and payment initiation."""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        box_choice = request.POST.get('box_choice')

        # Validate phone number
        if not phone_number or not validate_phone_number(phone_number):
            return JsonResponse({'error': 'Invalid phone number. Use a valid Safaricom number (07xxxxxxxx).'}, status=400)

        # Validate box choice dynamically
        rewards = generate_rewards()
        if box_choice not in rewards.keys():
            return JsonResponse({'error': 'Invalid box choice. Choose a valid option.'}, status=400)

        amount = 2  # Set the payment amount
        callback_url = settings.CALLBACK_URL

        try:
            # Initiate M-Pesa payment
            payment_response = initiate_mpesa_payment(phone_number, amount=amount, callback_url=callback_url)

            if 'error' in payment_response:
                logger.error(f"Payment initiation failed: {payment_response['error']}")
                return JsonResponse({'error': payment_response['error']}, status=400)

            # Save the transaction to the Payment model
            transaction = Payment.objects.create(
                user=request.user,
                phone_number=phone_number,
                amount=amount,
                status="Pending",
                box_choice=box_choice,
            )

            logger.info(f"STK Push sent to {phone_number} for amount {amount}")

            return JsonResponse({
                'status': 'success',
                'message': 'STK Push has been sent. Enter your M-Pesa PIN to confirm.',
                'reward': ''  # Placeholder removed
            })
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            return JsonResponse({'error': 'An error occurred while processing your request.'}, status=500)

    return render(request, 'store/lucky_box.html')


@login_required
def confirm_payment(request):
    """Confirm the payment status and reveal reward upon successful payment."""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        box_choice = request.POST.get('box_choice')

        if not phone_number or not box_choice:
            return JsonResponse({'error': 'Phone number and box choice are required.'}, status=400)

        transaction = Payment.objects.filter(phone_number=phone_number, status="Pending").first()

        if not transaction:
            return JsonResponse({'error': 'No pending transaction found for this phone number.'}, status=400)

        try:
            # Verify payment status with M-Pesa
            if not check_mpesa_payment_status(transaction):
                return JsonResponse({'error': 'Payment not completed. Please try again.'}, status=400)

            # Update transaction status
            transaction.status = "Completed"
            transaction.save()

            # Assign a reward
            rewards = generate_rewards()
            selected_reward = rewards.get(box_choice, 0)  # Ensure numeric reward

            # Create a RewardPayment entry
            reward_entry, created = RewardPayment.objects.get_or_create(
                user=transaction.user,
                phone_number=phone_number,
                amount=transaction.amount,
                transaction_id=transaction.id,  # Use Payment ID as transaction_id
                is_successful=True,
                reward=selected_reward,
                payment=transaction
            )

            logger.info(f"Payment confirmed for {phone_number}. Reward: {selected_reward}")

            return JsonResponse({
                'message': f'Payment successful! Your reward is: {selected_reward}',
                'reward': selected_reward
            })
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return JsonResponse({'error': 'An error occurred while confirming your payment.'}, status=500)


def generate_rewards():
    """Generate random rewards for each box dynamically."""
    return {
        "1": random.choice([10, 20, 50]),
        "2": random.choice([30, 40, 60]),
        "3": random.choice([70, 80, 90]),
    }


def check_mpesa_payment_status(transaction):
    """
    Simulates checking the payment status from M-Pesa.
    Replace this function with actual M-Pesa API verification logic.
    """
    return True  # Assume payment is successful for now
