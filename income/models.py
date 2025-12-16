from django.db import models
from django.contrib.auth.models import User


class CategoryChoice(models.TextChoices):
    GIFT = "GIFT", "Gift"
    SALARY = "SALARY", "Salary"
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
