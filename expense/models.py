from django.db import models
from django.contrib.auth.models import User


# ==========================
# EXPENSE CATEGORY CHOICES
# ==========================
class ExpenseCategoryChoice(models.TextChoices):

    RENT = "RENT", "House Rent"
    HOUSE_EXP = "HOUSE_EXP", "House Expenses"
    INTERNET = "INTERNET", "Internet / WiFi"
    MOBILE = "MOBILE", "Mobile Recharge / Bill"

    GROCERIES = "GROCERIES", "Groceries"
    FOOD = "FOOD", "Food"

    VEHICLE = "VEHICLE", "Vehicle"

    MEDICAL = "MEDICAL", "Medical Expenses"
    HEALTH_INSURANCE = "HEALTH_INSURANCE", "Health Insurance"

    EDUCATION = "EDUCATION", "Education"

    CLOTHING = "CLOTHING", "Clothing"
    FOOTWEAR = "FOOTWEAR", "Footwear"

    MOVIE = "MOVIE", "Movies"

    ONLINE_SHOPPING = "ONLINE_SHOPPING", "Online Shopping"

    CREDIT_CARD = "CREDIT_CARD", "Credit Card Payment"
    BANK_CHARGES = "BANK_CHARGES", "Bank Charges"

    GIFT = "GIFT", "Gift"
    DONATION = "DONATION", "Donation"

    TRAVEL = "TRAVEL", "Travel / Trip"

    OTHERS = "OTHERS", "Others"


# ==========================
# EXPENSE MODEL
# ==========================
class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    expense_id = models.CharField(max_length=10, primary_key=True)

    title = models.CharField(max_length=100)

    category = models.CharField(
        max_length=100,                     # ✔ Safe length
        choices=ExpenseCategoryChoice.choices
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
