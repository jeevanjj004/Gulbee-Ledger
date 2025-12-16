from django import forms
from income.models import Income
class incomeForm(forms.ModelForm):

    class Meta:
        model=Income
        fields=["source","category","date","amount","notes"]

class updateIncomeForm(forms.ModelForm):

    class Meta:
        model=Income
        fields=["source","category","date","amount","notes"]