from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from .models import Income,CategoryChoice
from .forms import incomeForm,updateIncomeForm
from datetime import datetime
import random
from django.db.models import Sum

# Create your views here.


def view_all_income(request):
    income=Income.objects.filter(user=request.user).order_by("date")
    total_income_dict = income.aggregate(total=Sum("amount"))  # calculate total dynamically
    total_income = total_income_dict['total'] or 0  # if no records, total=0
    print(total_income_dict)
    return render(request,"view_income.html",{"income":income,"total_income":total_income})

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
def delete_income(request,pk):
    income=get_object_or_404(Income,income_id=pk)
    if request.method=="POST":
        income.delete()
        return redirect("view_all_income")
    return render(request, "confirm_delete.html", {"income": income})



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
