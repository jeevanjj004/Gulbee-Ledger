from django import forms
from .models import Expense
class createExpenseForm(forms.ModelForm):
    class Meta:
        model=Expense
        fields=["title","category", "date", "amount", "paid_to", "notes", "bill_photo"]

class updateExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ["title", "category", "date", "amount", "paid_to", "notes", "bill_photo"]