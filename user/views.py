from django.shortcuts import render,redirect
from .forms import addUserForm
from django.contrib import messages
from datetime import datetime
from django.urls import reverse

from django.http import JsonResponse

from django.contrib.auth import authenticate, login as auth_login, logout
from income.models import Income
from emi.models import EMI,EmiStatus
from expense.models import Expense
from debit.models import Debit
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.conf import settings
import random
from django.views.decorators.http import require_POST


# Create your views here.
def create_user(request):
    form=addUserForm(request.POST or None)
    if request.method=="POST":
        
        password=request.POST.get("password")
        confirm_password=request.POST.get("confirm_password")
        if password!=confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, "add_user.html", {"form": form})
            
        if form.is_valid():
            new_user=form.save(commit=False)
            new_user.set_password(password)

            new_user.username=form.cleaned_data["email"]
            new_user.date_joined = datetime.now()
            new_user.save()
            return redirect("login")
    return render(request,"add_user.html",{"form":form})



@require_POST
def logout_view(request):
    """
    Secure logout view:
    - Only accepts POST requests
    - Logs out the user
    - Shows a success message
    - Redirects to login page
    """
    logout(request)
    return redirect('login')  # Replace 'login' with your login URL name



def user_login(request):

    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return JsonResponse({
                "status": "error",
                "message": "Both username and password are required"
            }, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return JsonResponse({
                "status": "success",
                "message": "Login successful",
                "redirect_url": reverse("home")
            })

        return JsonResponse({
            "status": "error",
            "message": "Invalid username or password"
        }, status=401)

    return render(request, "login.html")

@login_required
def home(request):
    user = request.user

    # ---- TOTAL INCOME ----
    total_income = (
        Income.objects
        .filter(user=user)
        .aggregate(total=Sum('amount'))['total']
        or 0
    )

    # ---- TOTAL EXPENSE ----
    total_expense = (
        Expense.objects
        .filter(user=user)
        .aggregate(total=Sum('amount'))['total']
        or 0
    )

    # ---- TOTAL DEBIT TAKEN ----
    total_debit = (
        Debit.objects
        .filter(user=user)
        .aggregate(total=Sum('amount'))['total']
        or 0
    )

    # ---- TOTAL EMI PAID ----
    total_paid_emi = (
        EMI.objects
        .filter(user=user, status=EmiStatus.PAID)
        .aggregate(total=Sum('amount'))['total']
        or 0
    )

    # ---- REMAINING DEBIT ----
    remaining_debit = max(total_debit - total_paid_emi, 0)

    # ---- NEAREST EMI (NEXT 2 DAYS) ----
    today = timezone.now().date()
    next_two_days = today + timedelta(days=2)

    nearest_emi_count = (
        EMI.objects
        .filter(
            user=user,
            status=EmiStatus.PENDING,
            due_date__range=(today, next_two_days)
        )
        .count()
    )
    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'remaining_debit': remaining_debit,
        'nearest_emi_count': nearest_emi_count,
    }

    return render(request, "home.html", context)


# ===============================
# Change Password (Logged-in user)
# ===============================
@login_required
def change_password(request):
    context = {}

    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        if not user.check_password(current_password):
            context["error"] = "Current password is incorrect"
            return render(request, "change_password.html", context)

        if new_password != confirm_password:
            context["error"] = "New password and confirm password do not match"
            return render(request, "change_password.html", context)

        user.set_password(new_password)
        user.save()

        context["success"] = "Password changed successfully. Please login again."
        return redirect("login")

    return render(request, "change_password.html", context)


@login_required
def profile(request):
    return render(request,"profile.html")












#password changing forget by mail otp

OTP_EXPIRY_MINUTES = 5  # OTP valid duration

# ==================== Forgot Password ====================
def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST.get("email").strip()
        users = User.objects.filter(email=email)
        
        if not users.exists():
            messages.error(request, "No user registered with this email.")
            return redirect('forgot_password')
        
        # pick first user if multiple exist
        user = users.first()
        
        # generate OTP
        otp = random.randint(100000, 999999)
        otp_created_at = datetime.now()
        
        # save OTP in session
        request.session['otp'] = otp
        request.session['otp_user_id'] = user.id
        request.session['otp_created_at'] = otp_created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Send email with expiry info
        send_mail(
            subject="🔒 Your OTP for Password Reset",
            message=(
                f"Hello {user.first_name},\n\n"
                f"You requested a password reset. Your OTP is:\n\n"
                f"💡 {otp}\n\n"
                f"This OTP is valid for {OTP_EXPIRY_MINUTES} minutes.\n"
                f"If you did not request this, please ignore this email.\n\n"
                "Thank you,\nGULBEE LEDGER Team"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )
        
        messages.success(request, f"OTP sent to {email}. It will expire in {OTP_EXPIRY_MINUTES} minutes.")
        return redirect('verify_otp')
    
    return render(request, 'forgot_password.html')


# ==================== Verify OTP ====================
def verify_otp_view(request):
    if request.method == "POST":
        otp_input = request.POST.get("otp").strip()
        otp_session = request.session.get('otp')
        otp_created_at_str = request.session.get('otp_created_at')
        
        if not otp_session or not otp_created_at_str:
            messages.error(request, "OTP expired or not found. Please try again.")
            return redirect('forgot_password')
        
        otp_created_at = datetime.strptime(otp_created_at_str, '%Y-%m-%d %H:%M:%S')
        if datetime.now() > otp_created_at + timedelta(minutes=OTP_EXPIRY_MINUTES):
            # clear expired OTP
            request.session.pop('otp', None)
            request.session.pop('otp_user_id', None)
            request.session.pop('otp_created_at', None)
            messages.error(request, "OTP expired. Please request a new one.")
            return redirect('forgot_password')
        
        if str(otp_input) != str(otp_session):
            messages.error(request, "Invalid OTP. Try again.")
            return redirect('verify_otp')
        
        messages.success(request, "OTP verified! You can now reset your password.")
        return redirect('reset_password')
    
    return render(request, 'verify_otp.html')


# ==================== Reset Password ====================
def reset_password_view(request):
    if request.method == "POST":
        new_password = request.POST.get("password").strip()
        confirm_password = request.POST.get("confirm_password").strip()
        
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('reset_password')
        
        user_id = request.session.get('otp_user_id')
        if not user_id:
            messages.error(request, "Session expired. Try again.")
            return redirect('forgot_password')
        
        user = User.objects.get(id=user_id)
        user.password = make_password(new_password)
        user.save()
        
        # clear session data
        request.session.pop('otp', None)
        request.session.pop('otp_user_id', None)
        request.session.pop('otp_created_at', None)
        
        messages.success(request, "Password reset successful! You can login now.")
        return redirect('login')
    
    return render(request, 'reset_password.html')
