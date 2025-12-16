from django.shortcuts import render,redirect,get_list_or_404,get_object_or_404
from datetime import datetime,timedelta
import random
from .models import Debit,EmiCategory,InstallmentCategory,DebitStatus
from emi.models import EMI
from django.db.models import Sum
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.urls import reverse
from django.db.models import Sum, Q

def view_all_debit(request):
    debits = Debit.objects.filter(user=request.user)

    # ---- GET PARAMS ----
    search = request.GET.get("search")
    status = request.GET.get("status")
    is_emi = request.GET.get("is_emi")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    # ---- SEARCH ----
    if search:
        debits = debits.filter(
            Q(debit_id__icontains=search) |
            Q(lender_name__icontains=search)
        )

    # ---- STATUS FILTER ----
    if status:
        debits = debits.filter(status=status)

    # ---- EMI FILTER ----
    if is_emi == "yes":
        debits = debits.filter(is_emi=True)
    elif is_emi == "no":
        debits = debits.filter(is_emi=False)

    # ---- DATE FILTER ----
    if start_date:
        debits = debits.filter(start_date__gte=start_date)

    if end_date:
        debits = debits.filter(start_date__lte=end_date)

    debits = debits.order_by("-created_at")

    total_principal = debits.aggregate(total=Sum("amount"))["total"] or 0

    # 🔥 DROPDOWN DATA FROM BACKEND
    status_choices = [(s, s) for s in DebitStatus]
    emi_choices = [
        ("yes", "EMI"),
        ("no", "No EMI")
    ]

    context = {
        "debits": debits,
        "total_principal": total_principal,
        "status_choices": status_choices,
        "emi_choices": emi_choices,
    }
    return render(request, "view_all_debit.html", context)


def create_debit(request):
    if request.method == "POST":

        # BASIC
        lender_name = request.POST.get("lender_name")
        principal_amount = float(request.POST.get("principal_amount"))
        start_date = datetime.strptime(
            request.POST.get("start_date"), "%Y-%m-%d"
        ).date()
        notes = request.POST.get("notes")
        user = request.user

        is_emi = True if request.POST.get("is_emi") == "on" else False

        # DEFAULTS
        emi_type = EmiCategory.NO
        installment_frequency = InstallmentCategory.WEEKLY
        n_installments = 0
        emi_interest_rate = 0.0
        emi_amount = 0.0
        if is_emi:
            emi_type = request.POST.get("emi_type")
            installment_frequency = request.POST.get("installment_frequency")
            installments_str = request.POST.get("installments")

            if not emi_type or emi_type == EmiCategory.NO:
                messages.error(request, "Select a valid EMI type.")
                return redirect("add_debit")

            if not installment_frequency:
                messages.error(request, "Select installment frequency.")
                return redirect("add_debit")

            if not installments_str or int(installments_str) <= 0:
                messages.error(request, "Number of installments must be greater than 0.")
                return redirect("add_debit")

            n_installments = int(installments_str)

            # CUSTOM EMI
            if emi_type == EmiCategory.CUSTOM:
                emi_amt_str = request.POST.get("emi_amt")
                if not emi_amt_str or float(emi_amt_str) <= 0:
                    messages.error(request, "Enter valid custom EMI amount.")
                    return redirect("add_debit")

                emi_amount = float(emi_amt_str)

                # ✅ CUSTOM-ONLY VALIDATION
                if principal_amount <= (n_installments * emi_amount):
                    messages.error(
                        request,
                        "Principal amount must be greater than total EMI amount for Custom EMI."
                    )
                    return redirect("add_debit")

            # SHORT / LONG TERM
            else:
                interest_str = request.POST.get("emi_interest_rate")
                if not interest_str:
                    messages.error(request, "Enter EMI interest rate.")
                    return redirect("add_debit")

                emi_interest_rate = float(interest_str)

                emi_amount = emi_amount_fn(
                    emi_type,
                    emi_interest_rate,
                    principal_amount,
                    n_installments,
                )

        # COMMON SAVE
        debit_id = debit_id_fn()
        maturity_date = maturity_date_fn(
            start_date, n_installments, installment_frequency
        )

        now = datetime.now()
        status = "PENDING"

        Debit.objects.create(
            user=user,
            debit_id=debit_id,
            lender_name=lender_name,
            amount=principal_amount,
            interest_percent=emi_interest_rate,
            start_date=start_date,
            maturity_date=maturity_date,
            is_emi=is_emi,
            emi_type=emi_type,
            emi_period=n_installments,
            installment_type=installment_frequency,
            emi_amount=emi_amount,
            status=status,
            notes=notes,
            created_at=now,
            updated_at=now,
        )

        # FIRST EMI
        if is_emi:
            if installment_frequency == InstallmentCategory.MONTHLY:
                due_date = start_date + relativedelta(months=1)
            else:
                due_date = start_date + relativedelta(weeks=1)

            EMI.objects.create(
                user=user,
                emi_id=emi_id_fn(),
                debit_id=debit_id,
                sequence_number=1,
                amount=emi_amount,
                due_date=due_date,
                paid_date=None,
                status="PENDING",
            )

        return render(
    request,
    "debit_success.html",
    {
        "redirect_url": reverse("view_all"),
        "message": "Debit created successfully"
    }
)


    context = {
        "emi_types": EmiCategory.choices,
        "installment_types": InstallmentCategory.choices,
    }
    return render(request, "add_debit.html", context)

def debit_id_fn():
    while True:
        num = random.randint(10000, 99999)
        id=f"DB{num}"
        if not Debit.objects.filter(debit_id=id).exists():
            return id
def emi_id_fn():
    while True:
        num = random.randint(10000, 99999)
        id=f"EMI{num}"
        if not EMI.objects.filter(emi_id=id).exists():
            return id

def emi_amount_fn(emi_type,emi_interest_rate,principal_amount,n_installments):
    if emi_type=="SHORT_TERM":
        interest=float(principal_amount*emi_interest_rate/100)
        emi_amount=(principal_amount+interest)/n_installments
        return emi_amount
    if emi_type=="LONG_TERM":
        interest=float(principal_amount*emi_interest_rate/100)
        emi_amount=interest
        return emi_amount
    

def maturity_date_fn(start_date,n_installments,installment_frequency):
    if installment_frequency=="WEEKLY":
        maturity_date=start_date+relativedelta(weeks=n_installments)
        return maturity_date  
    if installment_frequency=="MONTHLY":
        maturity_date=start_date+relativedelta(months=n_installments)
        return maturity_date   


# def total_payable_amount_fn(principal_amount,interest_rate,start_date,emi_type,emi_period):
#     end_date = start_date + relativedelta(months=emi_period)
#     if(emi_type=="NO" and interest_rate==0):
#         total_payable_amount=principal_amount
#     if(emi_type=="SHORT_TERM"):
#         interest=(interest_rate*principal_amount/100)
#         total_payable_amount=principal_amount+interest
        
#     return total_payable_amount

def delete_debit(request,pk):
    debit=get_object_or_404(Debit,debit_id=pk)
    if request.method=="POST":
        debit.delete()
        return redirect("view_all")
    return render(request, "debit_confirm_delete.html", {"debit": debit})

def update_debit(request, pk):
    debit = get_object_or_404(Debit, debit_id=pk)
    popup_message = None  # initialize variable

    # Check first EMI
    first_emi = EMI.objects.filter(debit=debit, sequence_number=1).first()
    if first_emi and first_emi.status == "PAID":
        return render(request, "update_debit.html", {
            "debit": debit,
            "popup_message": "Cannot edit this debit because the first EMI is already paid."
        })

    if request.method == "POST":
        lender_name = request.POST.get("lender_name")
        principal_amount_str = request.POST.get("principal_amount")
        start_date_str = request.POST.get("start_date")
        notes = request.POST.get("notes")
        is_emi = True if request.POST.get("is_emi") == "on" else False

        # --- VALIDATIONS ---
        if not principal_amount_str or float(principal_amount_str) <= 0:
            return render(request, "update_debit.html", {"debit": debit,
                "popup_message": "Enter a valid principal amount."})
        principal_amount = float(principal_amount_str)

        if not start_date_str:
            return render(request, "update_debit.html", {"debit": debit,
                "popup_message": "Select a valid start date."})
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        # DEFAULTS
        emi_type = EmiCategory.NO
        installment_frequency = InstallmentCategory.WEEKLY
        n_installments = 0
        emi_interest_rate = 0.0
        emi_amount = 0.0

        if is_emi:
            emi_type = request.POST.get("emi_type")
            installment_frequency = request.POST.get("installment_frequency")
            installments_str = request.POST.get("installments")

            if not emi_type or emi_type == EmiCategory.NO:
                return render(request, "update_debit.html", {"debit": debit,
                    "popup_message": "Select a valid EMI type."})

            if not installment_frequency:
                return render(request, "update_debit.html", {"debit": debit,
                    "popup_message": "Select installment frequency."})

            if not installments_str or int(installments_str) <= 0:
                return render(request, "update_debit.html", {"debit": debit,
                    "popup_message": "Number of installments must be greater than 0."})
            n_installments = int(installments_str)

            if emi_type == EmiCategory.CUSTOM:
                emi_amt_str = request.POST.get("emi_amt")
                if not emi_amt_str or float(emi_amt_str) <= 0:
                    return render(request, "update_debit.html", {"debit": debit,
                        "popup_message": "Enter valid custom EMI amount."})
                emi_amount = float(emi_amt_str)

                if principal_amount <= (n_installments * emi_amount):
                    return render(request, "update_debit.html", {"debit": debit,
                        "popup_message": "Principal must be greater than total EMI for Custom EMI."})
            else:
                interest_str = request.POST.get("emi_interest_rate")
                if not interest_str:
                    return render(request, "update_debit.html", {"debit": debit,
                        "popup_message": "Enter EMI interest rate."})
                emi_interest_rate = float(interest_str)
                emi_amount = emi_amount_fn(emi_type, emi_interest_rate, principal_amount, n_installments)

        # --- UPDATE DEBIT ---
        maturity_date = maturity_date_fn(start_date, n_installments, installment_frequency)
        now = datetime.now()
        status = "PENDING"

        debit.user = request.user
        debit.lender_name = lender_name
        debit.amount = principal_amount
        debit.interest_percent = emi_interest_rate
        debit.start_date = start_date
        debit.maturity_date = maturity_date
        debit.is_emi = is_emi
        debit.emi_type = emi_type
        debit.emi_period = n_installments
        debit.installment_type = installment_frequency
        debit.emi_amount = emi_amount
        debit.status = status
        debit.notes = notes
        debit.updated_at = now
        debit.save()

        # --- RESET FIRST EMI ---
        if is_emi:
            if installment_frequency == InstallmentCategory.MONTHLY:
                first_emi_due_date = start_date + relativedelta(months=1)
            else:
                first_emi_due_date = start_date + relativedelta(weeks=1)

            if first_emi:
                first_emi.user = request.user
                first_emi.sequence_number = 1
                first_emi.amount = emi_amount
                first_emi.due_date = first_emi_due_date
                first_emi.paid_date = None
                first_emi.status = "PENDING"
                first_emi.save()
            else:
                EMI.objects.create(
                    user=request.user,
                    emi_id=emi_id_fn(),
                    debit=debit,
                    sequence_number=1,
                    amount=emi_amount,
                    due_date=first_emi_due_date,
                    paid_date=None,
                    status="PENDING"
                )

        return redirect("view_all")

    context = {
        "debit": debit,
        "emi_types": EmiCategory.choices,
        "installment_types": InstallmentCategory.choices,
        "existing_emis": EMI.objects.filter(debit=debit).order_by('sequence_number'),
        "popup_message": popup_message if 'popup_message' in locals() else None,
    }
    return render(request, "update_debit.html", context)
