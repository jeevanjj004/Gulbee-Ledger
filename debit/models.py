from django.db import models

from django.contrib.auth.models import User

class DebitStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    COMPLETED = "COMPLETED", "Completed"
    OVERDUE = "OVERDUE", "Overdue"

class EmiCategory(models.TextChoices):
    NO="NO","No"
    SHORT_TERM="SHORT_TERM","Short_term"
    LONG_TERM="LONG_TERM","Long_term"
    CUSTOM="CUSTOM","Custom"

class InstallmentCategory(models.TextChoices):
    MONTHLY="MONTHLY","Monthly"
    WEEKLY="WEEKLY","Weekly"


class Debit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    debit_id = models.CharField(max_length=10, primary_key=True)

    lender_name = models.CharField(max_length=100)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interest_percent = models.DecimalField(max_digits=5, decimal_places=2)

    start_date = models.DateField()
    maturity_date = models.DateField(null=True, blank=True)

    # EMI settings
    is_emi = models.BooleanField(default=False)
    emi_type = models.CharField(
        max_length=20,
        choices=EmiCategory.choices,
        default=EmiCategory.NO
    )
    emi_period = models.IntegerField(default=0)
    installment_type = models.CharField(
        max_length=20,
        choices=InstallmentCategory.choices,
        default=InstallmentCategory.WEEKLY
    )
    emi_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=DebitStatus.choices,
        default=DebitStatus.PENDING
    )

    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.debit_id} - {self.lender_name}"
