from django.urls import path
from store.views.login import login_view, logout_view
from store.views.register import register_view
from store.views.password_reset import password_reset_view, password_reset_done_view, password_reset_confirm_view
from store.views.lucky_box import lucky_box
from store.views.home import home  # Import the home view
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

app_name = 'store'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Add home view
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('password_reset/', password_reset_view, name='password_reset'),
    path('password_reset_done/', password_reset_done_view, name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('lucky-box/', lucky_box, name='lucky_box'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)