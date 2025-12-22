from django.db import models
from django.contrib.auth.models import User


class CategoryChoice(models.TextChoices):
   
    SALARY = "SALARY", "Salary"
    BONUS = "BONUS", "Bonus"
    COMMISSION = "COMMISSION", "Commission"
    FREELANCE = "FREELANCE", "Freelance / Contract"

    BUSINESS = "BUSINESS", "Business Income"
    CONSULTING = "CONSULTING", "Consulting"
    PROFIT = "PROFIT", "Business Profit"

    INTEREST = "INTEREST", "Interest"
    RENTAL = "RENTAL", "Rental Income"
    CAPITAL_GAIN = "CAPITAL_GAIN", "Capital Gain"

    GIFT = "GIFT", "Gift"
    DONATION = "DONATION", "Donation Received"
    REFUND = "REFUND", "Refund"
    CASHBACK = "CASHBACK", "Cashback"
    PRIZE = "PRIZE", "Prize / Lottery"

    PENSION = "PENSION", "Pension"
    SUBSIDY = "SUBSIDY", "Government Subsidy"
    SCHOLARSHIP = "SCHOLARSHIP", "Scholarship"

    YOUTUBE = "YOUTUBE", "YouTube Income"
    BLOG = "BLOG", "Blog / Content"
    ONLINE_SALES = "ONLINE_SALES", "Online Sales"


    OTHERS = "OTHERS", "Others"

class Income(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    income_id = models.CharField(max_length=7, primary_key=True)
    category = models.CharField(max_length=20, choices=CategoryChoice.choices)
    source = models.CharField(max_length=100)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField()  # auto when created
    updated_at = models.DateTimeField()      # auto on every update

    def __str__(self):
        return f"{self.income_id} - {self.source}"
