from django.db import models
from debit.models import Debit   # adjust import based on your project structure

from django.contrib.auth.models import User

class EmiStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    PAID = "PAID", "Paid"
    OVERDUE = "OVERDUE", "Overdue"

class EMI(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    emi_id = models.CharField(max_length=10, primary_key=True)

    debit = models.ForeignKey(Debit, on_delete=models.CASCADE)

    sequence_number = models.IntegerField()   # 1, 2, 3....

    amount = models.DecimalField(max_digits=10, decimal_places=2)

    due_date = models.DateField()
    
    paid_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=EmiStatus.choices,
        default=EmiStatus.PENDING
    )

    bill_photo = models.ImageField(
        upload_to="emibills/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.emi_id} - {self.debit.debit_id}"
