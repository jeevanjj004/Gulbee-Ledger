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
