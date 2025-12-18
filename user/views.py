from django.shortcuts import render,redirect
from .forms import addUserForm
from django.contrib import messages
import datetime
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
            new_user.date_joined=datetime.datetime.now()
            new_user.save()
            return redirect("login")
    return render(request,"add_user.html",{"form":form})

def user_login(request):

    if request.method == "POST":
        username = request.POST.get("username")  # get validated username/email
        password = request.POST.get("password")   # get validated password

        user = authenticate(request, username=username, password=password)
        if user:
            l=auth_login(request, user)  # do NOT use the same function name
            if l:
                print("logined")
            else:
                print("login error")
            return redirect("home")
        else:
            messages.error(request, "Username or password is incorrect")

    return render(request, "login.html")

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
        return render(request, "change_password.html", context)

    return render(request, "change_password.html", context)


# # ===============================
# # Forget Password (Email reset)
# # ===============================
# def forget_password(request):
#     context = {}

#     if request.method == "POST":
#         email = request.POST.get("email")

#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             context["error"] = "No account found with this email"
#             return render(request, "forget_password.html", context)

#         # Generate random password
#         random_password = get_random_string(length=8)
#         user.set_password(random_password)
#         user.save()

#         send_mail(
#             subject="Gulbee Ledger - Password Reset",
#             message=f"""
# Hello {user.username},

# Your new temporary password is:

# {random_password}

# Please login and change your password immediately.
# """,
#             from_email="internshipidk456@gmail.com",
#             recipient_list=[email],
#             fail_silently=False,
#         )

#         context["success"] = "New password sent to your email"
#         return render(request, "forget_password.html", context)

#     return render(request, "forget_password.html", context)


def profile(request):
    return render(request,"profile.html")