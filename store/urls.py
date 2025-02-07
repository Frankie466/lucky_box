from django.urls import path
from .views.home import home_view  # Import your home view
from .views.login import login_view, logout_view
from .views.register import register_view
from .views.password_reset import password_reset_view, password_reset_done_view, password_reset_confirm_view
from .views.lucky_box import lucky_box
from .views.mpesa import mpesa_callback_view  # Import the mpesa_callback_view

 
app_name = 'store'

urlpatterns = [
    path('', home_view, name='home'),  # Add this line for the home route
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('password_reset/', password_reset_view, name='password_reset'),
    path('password_reset_done/', password_reset_done_view, name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('lucky-box/', lucky_box, name='lucky_box'),
    path('mpesa-callback/', mpesa_callback_view, name='mpesa_callback'),  # Add this line for M-Pesa callback
    
]

