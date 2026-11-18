from django.urls import path, include
from users import views as views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('users/signup', views.signup, name='signup'),
    path('users/profile', views.profile, name='profile'),
    path('users/confirm/logout', views.logoutconfirm, name='logoutconfirm'),
    path('users/login', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('users/logout', auth_views.LogoutView.as_view(template_name='users/logout.html'), name='logout'),
    path('users/forgot-password', views.forgot_password, name='forgot_password'),
    path('users/verify-otp', views.verify_otp, name='verify_otp'),
    path('users/reset-password', views.reset_password, name='reset_password'),
    path('users/resend-otp', views.resend_otp, name='resend_otp'),
]