from django.shortcuts import render, redirect
from store.models.user import CustomUser  # Import the custom user model
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        phone_number = request.POST.get('phone_number')

        context = {
            'username': username,
            'phone_number': phone_number,
        }

        # Check for empty fields
        if not username or not password or not password_confirm or not phone_number:
            messages.error(request, 'All fields are required.')
            return render(request, 'store/register.html', context)

        if password != password_confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'store/register.html', context)

        try:
            # Validate the password
            validate_password(password)

            # Create the user
            user = CustomUser.objects.create_user(username=username, password=password, phone_number=phone_number)
            user.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('store:login')
        except ValidationError as e:
            messages.error(request, f'Password error: {" ".join(e.messages)}')
        except CustomUser.DoesNotExist:
            messages.error(request, 'Error creating user. Please try again.')
        except Exception as e:
            messages.error(request, f'Unexpected error: {str(e)}')

        return render(request, 'store/register.html', context)

    return render(request, 'store/register.html')
