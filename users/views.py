import random
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from .forms import UserUpdateForm, CustomUserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# Create your views here.
def signup(request):
    form = CustomUserCreationForm()

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'users/signup.html', context)

def profile(request):
    form = UserUpdateForm(instance=request.user)

    if request.method == 'POST': 
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form':form}
    return render(request, 'users/profile.html',context)

def logoutconfirm(request):
    return render(request,'users/logoutconfirm.html')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(
                request,
                'users/forgot_password.html',
                {'error': 'No account found with this email address.'}
            )

        otp = random.randint(100000, 999999)

        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        request.session['otp_created_at'] = datetime.now().isoformat()
        request.session['otp_attempts'] = 0
        request.session['otp_sent_at'] = datetime.now().isoformat()

        send_mail(
            'BlogPost Password Reset OTP',
            f'Your OTP for resetting your BlogPost password is: {otp}',
            None,
            [email],
            fail_silently=False,
        )

        return redirect('verify_otp')

    return render(request, 'users/forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')

        stored_otp = request.session.get('reset_otp')
        otp_created_at = request.session.get('otp_created_at')
        attempts = request.session.get('otp_attempts', 0)

        if not stored_otp or not otp_created_at:
            return render(
                request,
                'users/verify_otp.html',
                {
                    'error': 'OTP is invalid or has expired. Please request a new OTP.'
                }
            )

        created_time = datetime.fromisoformat(otp_created_at)
        current_time = datetime.now()

        # Check OTP expiration
        if current_time - created_time > timedelta(minutes=5):
            request.session.pop('reset_otp', None)
            request.session.pop('otp_created_at', None)
            request.session.pop('otp_attempts', None)

            return render(
                request,
                'users/verify_otp.html',
                {
                    'error': 'OTP has expired. Please request a new OTP.'
                }
            )

        # Check whether OTP is correct
        if entered_otp == str(stored_otp):
            request.session['otp_verified'] = True

            request.session.pop('reset_otp', None)
            request.session.pop('otp_created_at', None)
            request.session.pop('otp_attempts', None)

            return redirect('reset_password')

        # Wrong OTP
        attempts += 1
        request.session['otp_attempts'] = attempts

        # Maximum 3 attempts
        if attempts >= 3:
            request.session.pop('reset_otp', None)
            request.session.pop('otp_created_at', None)
            request.session.pop('otp_attempts', None)

            return render(
                request,
                'users/verify_otp.html',
                {
                    'error': 'Too many incorrect attempts. Please request a new OTP.'
                }
            )

        remaining_attempts = 3 - attempts

        return render(
            request,
            'users/verify_otp.html',
            {
                'error': f'Invalid OTP. You have {remaining_attempts} attempt(s) remaining.'
            }
        )

    return render(request, 'users/verify_otp.html')

def resend_otp(request):
    email = request.session.get('reset_email')

    if not email:
        return redirect('forgot_password')

    otp_sent_at = request.session.get('otp_sent_at')

    if otp_sent_at:
        sent_time = datetime.fromisoformat(otp_sent_at)
        current_time = datetime.now()

        if current_time - sent_time < timedelta(seconds=30):
            return render(
                request,
                'users/verify_otp.html',
                {
                    'error': 'Please wait 30 seconds before requesting another OTP.'
                }
            )

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect('forgot_password')

    otp = random.randint(100000, 999999)

    request.session['reset_otp'] = otp
    request.session['otp_created_at'] = datetime.now().isoformat()
    request.session['otp_attempts'] = 0
    request.session['otp_sent_at'] = datetime.now().isoformat()
    request.session['otp_verified'] = False

    send_mail(
        'BlogPost Password Reset OTP',
        f'Your new OTP for resetting your BlogPost password is: {otp}',
        None,
        [email],
        fail_silently=False,
    )

    return redirect('verify_otp')

def reset_password(request):
    if not request.session.get('otp_verified'):
        return redirect('forgot_password')

    if request.method == 'POST':
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(
                request,
                'users/reset_password.html',
                {'error': 'Passwords do not match.'}
            )

        try:
            validate_password(password1)
        except ValidationError as error:
            return render(
                request,
                'users/reset_password.html',
                {'error': error.messages}
            )

        email = request.session.get('reset_email')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return redirect('forgot_password')

        user.set_password(password1)
        user.save()

        # Clear password reset session data
        request.session.pop('reset_email', None)
        request.session.pop('reset_otp', None)
        request.session.pop('otp_created_at', None)
        request.session.pop('otp_attempts', None)
        request.session.pop('otp_sent_at', None)
        request.session.pop('otp_verified', None)

        return redirect('login')

    return render(request, 'users/reset_password.html')