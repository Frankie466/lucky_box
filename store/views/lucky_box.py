import random
import logging
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from store.models.payment import Payment
from store.views.mpesa import initiate_mpesa_payment

logger = logging.getLogger(__name__)

@login_required
def lucky_box(request):
    """Handles the lucky box request and payment initiation."""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        box_choice = request.POST.get('box_choice')

        # Validate phone number
        if not phone_number or not phone_number.isdigit() or len(phone_number) != 10:
            return JsonResponse({'error': 'Invalid phone number. Ensure it is a 10-digit number.'}, status=400)

        # Validate box choice
        if box_choice not in ['1', '2', '3']:
            return JsonResponse({'error': 'Invalid box choice. Choose between 1, 2, or 3.'}, status=400)

        callback_url = settings.CALLBACK_URL
        amount = 42  # Payment amount can be modified as needed

        try:
            # Initiate the payment process
            payment_response = initiate_mpesa_payment(phone_number, amount=amount, callback_url=callback_url)

            # Check if the payment initiation was successful
            if 'error' in payment_response:
                logger.error(f"Payment initiation failed: {payment_response['error']}")
                return JsonResponse({'error': payment_response['error']}, status=400)

            # Save the transaction to the database
            transaction = Payment.objects.create(
                user=request.user,  # Associate payment with logged-in user
                phone_number=phone_number,
                amount=amount,
                status="Pending",
                box_choice=box_choice,
            )

            return JsonResponse({
                'status': 'success',
                'message': 'STK Push has been sent to your phone. Enter your M-Pesa pin to check your reward.',
                'reward': 'Reward will be revealed after payment completion.'  # Placeholder for the reward
            })
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            return JsonResponse({'error': 'An error occurred while processing your request.'}, status=500)

    # Render the lucky box page for GET requests
    return render(request, 'store/lucky_box.html')


@login_required
def confirm_payment(request):
    """Confirm the payment status and reward selection."""
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        box_choice = request.POST.get('box_choice')

        # Validate phone number and box choice
        if not phone_number or not box_choice:
            return JsonResponse({'error': 'Phone number and box choice are required.'}, status=400)

        # Fetch the pending transaction
        transaction = Payment.objects.filter(phone_number=phone_number, status="Pending").first()

        if not transaction:
            return JsonResponse({'error': 'No pending transaction found for this phone number.'}, status=400)

        try:
            # Check the payment status from M-Pesa (replace with actual logic)
            payment_status = check_mpesa_payment_status(transaction)

            if payment_status:
                # Update transaction status to "Completed"
                transaction.status = "Completed"

                # Generate and assign a reward
                all_rewards = generate_rewards()
                selected_reward = all_rewards.get(box_choice)

                # Assign the reward to the transaction
                transaction.reward = selected_reward
                transaction.save()

                return JsonResponse({
                    'message': f'Payment successful! Your reward is: {selected_reward}.',
                    'reward': selected_reward  # Returning the selected reward to display in UI
                })
            else:
                return JsonResponse({'error': 'Payment not completed. Please try again.'}, status=400)
        except Exception as e:
            logger.error(f"Error confirming payment: {str(e)}")
            return JsonResponse({'error': 'An error occurred while confirming your payment.'}, status=500)


def generate_rewards():
    """Generate random rewards for each box."""
    rewards = {
        "1": random.choice(["Ksh.10", "Ksh.20", "Ksh.50"]),
        "2": random.choice(["Ksh.30", "Ksh.40", "Ksh.60"]),
        "3": random.choice(["Ksh.70", "Ksh.80", "Ksh.90"]),
    }
    return rewards


def check_mpesa_payment_status(transaction):
    """
    Simulates checking the payment status from M-Pesa.
    Replace this function with actual M-Pesa API verification logic.
    """
    # TODO: Implement real M-Pesa payment verification
    return True  # Assume payment is successful for now
