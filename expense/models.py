from django.db import models

from django.contrib.auth.models import User

class ExpenseCategory(models.TextChoices):
    VENUE = "VENUE", "Venue"
    FOOD = "FOOD", "Food / Catering"
    DECORATION = "DECORATION", "Decoration"
    GIFT = "GIFT", "Gift"
    TRAVEL = "TRAVEL", "Travel"
    OTHERS = "OTHERS", "Others"



class Expense(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    expense_id = models.CharField(max_length=10, primary_key=True)

    title = models.CharField(max_length=100)

    category = models.CharField(
        max_length=30,
        choices=ExpenseCategory.choices
    )

    date = models.DateField()

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    paid_to = models.CharField(max_length=100)

    notes = models.TextField(blank=True, null=True)

    bill_photo = models.ImageField(
        upload_to="bills/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.expense_id} - {self.title}"
