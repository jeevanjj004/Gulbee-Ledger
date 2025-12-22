from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import Income,CategoryChoice
from .forms import incomeForm,updateIncomeForm
from datetime import datetime
import random
from django.db.models import Sum,Q
from django.contrib.auth.decorators import login_required

# Create your views here.

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum
from django.contrib.auth.decorators import login_required
from .models import Income, CategoryChoice  # Import CategoryChoice too

@login_required
def view_all_income(request):
    # Start with base queryset
    income_list = Income.objects.filter(user=request.user)
    
    # Get filter parameters
    category = request.GET.get('category')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    amount_min = request.GET.get('amount_min')
    amount_max = request.GET.get('amount_max')
    source = request.GET.get('source')
    search = request.GET.get('search')
    
    # Apply category filter
    if category:
        income_list = income_list.filter(category=category)
    
    # Apply date range filter
    if date_from:
        income_list = income_list.filter(date__gte=date_from)
    if date_to:
        income_list = income_list.filter(date__lte=date_to)
    
    # Apply amount range filter
    if amount_min:
        try:
            amount_min = float(amount_min)
            income_list = income_list.filter(amount__gte=amount_min)
        except ValueError:
            messages.warning(request, "Invalid minimum amount value")
    
    if amount_max:
        try:
            amount_max = float(amount_max)
            income_list = income_list.filter(amount__lte=amount_max)
        except ValueError:
            messages.warning(request, "Invalid maximum amount value")
    
    # Apply source filter
    if source:
        income_list = income_list.filter(source__icontains=source)
    
    # Apply general search filter (combines with other filters)
    if search:
        income_list = income_list.filter(
            Q(source__icontains=search) |
            Q(notes__icontains=search) |
            Q(category__icontains=search)
        )
    
    # Calculate total income for filtered results
    total_income = income_list.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Order by most recent first
    income_list = income_list.order_by('-date', '-income_id')
    
    # Get categories from CategoryChoice class
    # Since you're using TextChoices, access it like this:
    categories = CategoryChoice.choices
    
    context = {
        'income': income_list,
        'total_income': total_income,
        'categories': categories,
    }
    
    return render(request, 'view_income.html', context)







@login_required
def add_income(request):
    form=incomeForm(request.POST or None)
    if request.method=="POST":

        if form.is_valid():
            new_income=form.save(commit=False)
            new_income.income_id=auto_income_id()
            new_income.created_at = datetime.now()
            new_income.updated_at = datetime.now()
            new_income.user=request.user
            new_income.save()
            return redirect("view_all_income")
        else:
            form=incomeForm()
    cat=CategoryChoice.choices

    return render(request,"add_income.html",{"form":form,"cat":cat})

def auto_income_id():
    while True:
        # Generate random 5-digit number
        num = random.randint(10000, 99999)
        # Prefix it with IN
        income_id = f"IN{num}"

        # Check if this ID already exists
        if not Income.objects.filter(income_id=income_id).exists():
            return income_id
        
@login_required
def delete_income(request,pk):
    income=get_object_or_404(Income,income_id=pk)
    if request.method=="POST":
        income.delete()
        return redirect("view_all_income")
    return render(request, "confirm_delete.html", {"income": income})


@login_required
def income_update(request, pk):
    # Get the Income object from DB
    inc = get_object_or_404(Income, income_id=pk)

    # Bind the form to the existing instance
    if request.method == "POST":
        form = updateIncomeForm(request.POST, instance=inc)
        if form.is_valid():
            updated_income=form.save(commit=False)  # updates automatically, updated_at handled by model
            updated_income.income_id=inc.income_id
            updated_income.created_at=inc.created_at
            updated_income.updated_at=datetime.now()
            updated_income.save()
            
            return redirect("view_all_income")
    else:
        # Pre-fill form with existing data
        form = updateIncomeForm(instance=inc)

    cat = CategoryChoice.choices

    return render(request, "update_income.html", {"form": form, "cat": cat, "inc": inc})
