from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, ExpenseCategory
from .forms import createExpenseForm, updateExpenseForm
from datetime import datetime
from django.db.models import Sum
import random

# AUTO ID FUNCTION
def auto_expense_id():
    while True:
        num = random.randint(10000, 99999)
        expense_id = f"EX{num}"
        if not Expense.objects.filter(expense_id=expense_id).exists():
            return expense_id


# VIEW ALL EXPENSES
def view_all_expense(request):
    expenses = Expense.objects.filter(user=request.user).order_by("date")
    total_expense_dict = expenses.aggregate(total=Sum("amount"))
    total_expense = total_expense_dict["total"] or 0
    return render(request, "view_expense.html", {"expenses": expenses, "total_expense": total_expense})


# ADD EXPENSE
def add_expense(request):
    form = createExpenseForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if form.is_valid():
            exp = form.save(commit=False)
            exp.expense_id = auto_expense_id()
            exp.user = request.user
            exp.created_at = datetime.now()
            exp.updated_at = datetime.now()
            exp.save()
            return redirect("view_all_expense")

    cat = ExpenseCategory.choices
    return render(request, "add_expense.html", {"form": form, "cat": cat})


# UPDATE EXPENSE
def update_expense(request, pk):
    exp = get_object_or_404(Expense, expense_id=pk)
    
    if request.method == "POST":
        form = updateExpenseForm(request.POST, request.FILES, instance=exp)
        if form.is_valid():
            updated_exp = form.save(commit=False)
            updated_exp.expense_id = exp.expense_id
            updated_exp.user = request.user
            updated_exp.created_at = exp.created_at
            updated_exp.updated_at = datetime.now()
            updated_exp.save()
            return redirect("view_all_expense")
    else:
        form = updateExpenseForm(instance=exp)

    return render(request, "update_expense.html", {"form": form, "exp": exp})


# DELETE EXPENSE
def delete_expense(request, pk):
    exp = get_object_or_404(Expense, expense_id=pk)
    
    if request.method == "POST":
        exp.delete()
        return redirect("view_all_expense")
    
    return render(request, "confirm_delete_expense.html", {"exp": exp})
