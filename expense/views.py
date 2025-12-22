from django.shortcuts import render, redirect, get_object_or_404
from .models import Expense, ExpenseCategoryChoice
from .forms import createExpenseForm, updateExpenseForm
from datetime import datetime
from django.db.models import Sum,Q
import random
from django.contrib.auth.decorators import login_required

# AUTO ID FUNCTION
def auto_expense_id():
    while True:
        num = random.randint(10000, 99999)
        expense_id = f"EX{num}"
        if not Expense.objects.filter(expense_id=expense_id).exists():
            return expense_id

@login_required
def view_all_expense(request):
    expenses = Expense.objects.filter(user=request.user)
    
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    date_sort = request.GET.get('date_sort', 'newest')
    amount_sort = request.GET.get('amount_sort', '')
    
    # Apply search filter - ONLY ID and TITLE
    if search_query:
        expenses = expenses.filter(
            Q(expense_id__icontains=search_query) |  # Search by expense ID
            Q(title__icontains=search_query)         # Search by title
        )
    
    # Apply sorting
    if date_sort == 'oldest':
        expenses = expenses.order_by('date')
    elif date_sort == 'newest':
        expenses = expenses.order_by('-date')
    
    if amount_sort == 'high':
        expenses = expenses.order_by('-amount')
    elif amount_sort == 'low':
        expenses = expenses.order_by('amount')
    
    # Calculate totals
    total_expense_dict = expenses.aggregate(total=Sum("amount"))
    total_expense = total_expense_dict["total"] or 0
    filtered_count = expenses.count()
    
    return render(request, "view_expense.html", {
        "expenses": expenses,
        "total_expense": total_expense,
        "filtered_count": filtered_count,
        "search_query": search_query,
        "date_sort": date_sort,
        "amount_sort": amount_sort,
    })
# ADD EXPENSE
@login_required
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

    cat = ExpenseCategoryChoice.choices
    return render(request, "add_expense.html", {"form": form, "cat": cat})


# UPDATE EXPENSE
@login_required
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
@login_required
def delete_expense(request, pk):
    exp = get_object_or_404(Expense, expense_id=pk)
    
    if request.method == "POST":
        exp.delete()
        return redirect("view_all_expense")
    
    return render(request, "confirm_delete_expense.html", {"exp": exp})
