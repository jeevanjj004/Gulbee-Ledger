from django.shortcuts import render,get_object_or_404,redirect
from .models import EMI
from dateutil.relativedelta import relativedelta
from datetime import date
from debit.views import emi_id_fn
from debit.models import Debit


from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
def view_emi(request):
    user = request.user
    emis = EMI.objects.filter(user=user).order_by("debit", "sequence_number")
    print(emis)
    print(user)
    return render(request, "view_all_emi.html", {"emis": emis})

def pay_emi(request, emi_id):
    emi = get_object_or_404(EMI, emi_id=emi_id)
    debit = emi.debit  # Related Debit object

    if request.method == "POST":
        # Mark current EMI as paid
        emi.status = "PAID"
        emi.paid_date = date.today()
        emi.save()

        # Create next EMI only if pending installments exist
        if emi.sequence_number < debit.emi_period:
            next_seq = emi.sequence_number + 1

            # Calculate next due date
            if debit.installment_type == "MONTHLY":
                next_due_date = emi.due_date + relativedelta(months=1)
            else:
                next_due_date = emi.due_date + relativedelta(weeks=1)

            # Create the next EMI record with status "PENDING"
            EMI.objects.create(
                user=request.user,
                emi_id=emi_id_fn(),
                debit=debit,
                sequence_number=next_seq,
                amount=debit.emi_amount,
                due_date=next_due_date,
                status="PENDING"   # <-- should be PENDING, not PAID
            )

        # Check after saving current EMI: if it’s the last, mark Debit completed
        if emi.sequence_number == debit.emi_period:
            debit.status = "COMPLETED"
            debit.save()

        return redirect("view_all_emi")

    return render(request, "pay_emi.html", {"emi": emi})

def emi_details(request, debit_id):
    # Get Debit info
    debit = Debit.objects.get(debit_id=debit_id)
    n_installment = debit.emi_period
    installment_type = debit.installment_type
    start_date = debit.start_date

    # All EMIs for this debit
    emis = EMI.objects.filter(debit_id=debit_id).order_by('sequence_number')

    # Generate EMI dates (if you want planned dates)
    emi_dates = {}
    temp = start_date
    for i in range(1, n_installment + 1):
        if installment_type == "MONTHLY":
            temp += relativedelta(months=1)
        elif installment_type == "WEEKLY":
            temp += relativedelta(weeks=1)
        emi_dates[i] = temp

    context = {
        "debit": debit,
        "emis": emis,
        "emi_dates": emi_dates,
    }

    return render(request, "emi_details.html", context)
