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
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

@login_required
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



@login_required
def create_debit(request):
    """
    Create a new debit record with optional EMI configuration.
    Handles both regular debits and EMI-based debits.
    """
    if request.method == "POST":
        try:
            # ================= VALIDATE REQUIRED FIELDS =================
            lender_name = request.POST.get("lender_name")
            principal_amount_str = request.POST.get("principal_amount")
            start_date_str = request.POST.get("start_date")
            
            # Validate required fields
            if not lender_name or not principal_amount_str or not start_date_str:
                return JsonResponse({
                    "status": "error",
                    "message": "All required fields must be filled"
                })
            
            # ================= PARSE AND VALIDATE DATA =================
            principal_amount = float(principal_amount_str)
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            notes = request.POST.get("notes", "")
            user = request.user
            
            # Validate principal amount
            if principal_amount <= 0:
                return JsonResponse({
                    "status": "error",
                    "message": "Principal amount must be greater than 0"
                })
            
            # ================= EMI CONFIGURATION =================
            is_emi = request.POST.get("is_emi") == "on"
            
            # Default values for non-EMI debits
            emi_type = EmiCategory.NO
            installment_frequency = InstallmentCategory.WEEKLY
            n_installments = 0
            emi_interest_rate = 0.0
            emi_amount = 0.0
            last_emi_amount = 0.0
            
            if is_emi:
                # ================= VALIDATE EMI FIELDS =================
                emi_type = request.POST.get("emi_type")
                installment_frequency = request.POST.get("installment_frequency")
                installments_str = request.POST.get("installments")
                
                # Validate EMI type selection
                if not emi_type or emi_type == EmiCategory.NO:
                    return JsonResponse({
                        "status": "error",
                        "message": "Select a valid EMI type"
                    })
                
                # Validate installment frequency
                if not installment_frequency:
                    return JsonResponse({
                        "status": "error",
                        "message": "Select installment frequency"
                    })
                
                # Validate number of installments
                if not installments_str:
                    return JsonResponse({
                        "status": "error",
                        "message": "Enter number of installments"
                    })
                
                n_installments = int(installments_str)
                if n_installments <= 0:
                    return JsonResponse({
                        "status": "error",
                        "message": "Number of installments must be greater than 0"
                    })
                
                # ================= CUSTOM EMI CALCULATION =================
                if emi_type == EmiCategory.CUSTOM:
                    different_last = request.POST.get("different_last_installment") == "on"
                    emi_amount_str = request.POST.get("emi_amt", "0")
                    
                    # Validate EMI amount
                    if not emi_amount_str:
                        return JsonResponse({
                            "status": "error",
                            "message": "Enter EMI amount for custom EMI"
                        })
                    
                    emi_amount = float(emi_amount_str)
                    if emi_amount <= 0:
                        return JsonResponse({
                            "status": "error",
                            "message": "EMI amount must be greater than 0"
                        })
                    
                    if different_last:
                        # Validate last installment amount
                        last_installment_amount_str = request.POST.get("last_installment_amount")
                        if not last_installment_amount_str:
                            return JsonResponse({
                                "status": "error",
                                "message": "Enter last installment amount"
                            })
                        
                        last_emi_amount = float(last_installment_amount_str)
                        if last_emi_amount <= 0:
                            return JsonResponse({
                                "status": "error",
                                "message": "Last installment amount must be greater than 0"
                            })
                        
                        # Calculate total: (n-1) regular installments + last installment
                        regular_total = emi_amount * (n_installments - 1)
                        total = regular_total + last_emi_amount
                        
                        # Validate total equals principal amount (allow 0.01 difference for rounding)
                        if abs(total - principal_amount) > 0.01:
                            return JsonResponse({
                                "status": "error",
                                "message": f"Total EMI amount (₹{total:.2f}) must equal principal amount (₹{principal_amount:.2f})"
                            })
                    else:
                        # All installments are equal
                        last_emi_amount = emi_amount
                        total = emi_amount * n_installments
                        
                        # Validate total equals principal amount
                        if abs(total - principal_amount) > 0.01:
                            return JsonResponse({
                                "status": "error",
                                "message": f"Total EMI amount (₹{total:.2f}) must equal principal amount (₹{principal_amount:.2f})"
                            })
                
                # ================= SHORT/LONG TERM EMI CALCULATION =================
                else:
                    # Validate interest rate for short/long term EMI
                    interest_rate_str = request.POST.get("emi_interest_rate")
                    if not interest_rate_str:
                        return JsonResponse({
                            "status": "error",
                            "message": "Enter interest rate for EMI"
                        })
                    
                    emi_interest_rate = float(interest_rate_str)
                    if emi_interest_rate < 0:
                        return JsonResponse({
                            "status": "error",
                            "message": "Interest rate cannot be negative"
                        })
                    
                    # Calculate EMI amount using the emi_amount_fn function
                    emi_amount = emi_amount_fn(
                        emi_type,
                        emi_interest_rate,
                        principal_amount,
                        n_installments
                    )
                    last_emi_amount = emi_amount
            
            # ================= GENERATE DEBIT ID AND MATURITY DATE =================
            debit_id = debit_id_fn()
            maturity_date = maturity_date_fn(
                start_date, n_installments, installment_frequency
            )
            
            # ================= CREATE DEBIT RECORD =================
            debit = Debit.objects.create(
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
                last_emi_amount=last_emi_amount,
                status="PENDING",
                notes=notes,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            
            # ================= CREATE FIRST EMI RECORD (if EMI-based) =================
            if is_emi:
                # Calculate first due date based on installment frequency
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
                    status="PENDING",
                )
            
            # ================= RETURN SUCCESS RESPONSE =================
              
# ================= RETURN SUCCESS RESPONSE =================
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return JsonResponse({
                    "status": "success",
                    "message": "Debit created successfully",
                    "redirect_url": reverse("view_all")
                })

            # fallback for normal form submit
            return redirect("view_all")          
        except ValueError as e:
            # Handle parsing errors (invalid numbers, dates, etc.)
            return JsonResponse({
                "status": "error",
                "message": f"Invalid data format: {str(e)}"
            })
        except Exception as e:
            # Handle any other unexpected errors
            return JsonResponse({
                "status": "error",
                "message": f"An unexpected error occurred: {str(e)}"
            })
    
    # ================= RENDER FORM FOR GET REQUESTS =================
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
@login_required
def delete_debit(request,pk):
    debit=get_object_or_404(Debit,debit_id=pk)
    if request.method=="POST":
        debit.delete()
        return redirect("view_all")
    return render(request, "debit_confirm_delete.html", {"debit": debit})


@login_required
def update_debit(request, pk):
    debit = get_object_or_404(Debit, debit_id=pk)

    # Block edit if first EMI is paid
    first_emi = EMI.objects.filter(debit=debit, sequence_number=1).first()
    if first_emi and first_emi.status == "PAID":
        return render(request, "update_debit.html", {
            "debit": debit,
            "popup_message": "Cannot edit this debit because the first EMI is already paid."
        })

    if request.method == "POST":
        lender_name = request.POST.get("lender_name")
        principal_amount = float(request.POST.get("principal_amount", 0))
        start_date = datetime.strptime(request.POST.get("start_date"), "%Y-%m-%d").date()
        notes = request.POST.get("notes", "")
        is_emi = request.POST.get("is_emi") == "on"

        if principal_amount <= 0:
            return render(request, "update_debit.html", {
                "debit": debit,
                "popup_message": "Principal amount must be greater than 0."
            })

        # Defaults
        emi_type = EmiCategory.NO
        installment_frequency = InstallmentCategory.WEEKLY
        n_installments = 0
        emi_interest_rate = 0.0
        emi_amount = 0.0
        last_emi_amount = 0.0

        if is_emi:
            emi_type = request.POST.get("emi_type")
            installment_frequency = request.POST.get("installment_frequency")
            n_installments = int(request.POST.get("installments", 0))

            if n_installments <= 0:
                return render(request, "update_debit.html", {
                    "debit": debit,
                    "popup_message": "Number of installments must be greater than 0."
                })

            # -------- CUSTOM EMI --------
            if emi_type == EmiCategory.CUSTOM:
                emi_amount = float(request.POST.get("emi_amt", 0))
                different_last = request.POST.get("different_last_installment") == "on"

                if emi_amount <= 0:
                    return render(request, "update_debit.html", {
                        "debit": debit,
                        "popup_message": "Enter valid EMI amount."
                    })

                if different_last:
                    last_emi_amount = float(request.POST.get("last_installment_amount", 0))
                    total = emi_amount * (n_installments - 1) + last_emi_amount
                else:
                    last_emi_amount = emi_amount
                    total = emi_amount * n_installments

                if abs(total - principal_amount) > 0.01:
                    return render(request, "update_debit.html", {
                        "debit": debit,
                        "popup_message": "Total EMI must equal principal amount."
                    })

            # -------- INTEREST EMI --------
            else:
                emi_interest_rate = float(request.POST.get("emi_interest_rate", 0))
                emi_amount = emi_amount_fn(
                    emi_type, emi_interest_rate, principal_amount, n_installments
                )
                last_emi_amount = emi_amount

        # Update Debit
        maturity_date = maturity_date_fn(start_date, n_installments, installment_frequency)

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
        debit.last_emi_amount = last_emi_amount
        debit.notes = notes
        debit.updated_at = datetime.now()
        debit.save()

        # Reset first EMI
        if is_emi:
            first_due_date = (
                start_date + relativedelta(months=1)
                if installment_frequency == InstallmentCategory.MONTHLY
                else start_date + relativedelta(weeks=1)
            )

            if first_emi:
                first_emi.amount = emi_amount
                first_emi.due_date = first_due_date
                first_emi.status = "PENDING"
                first_emi.paid_date = None
                first_emi.save()
            else:
                EMI.objects.create(
                    user=request.user,
                    emi_id=emi_id_fn(),
                    debit=debit,
                    sequence_number=1,
                    amount=emi_amount,
                    due_date=first_due_date,
                    status="PENDING"
                )

        return redirect("view_all")

    return render(request, "update_debit.html", {
        "debit": debit,
        "emi_types": EmiCategory.choices,
        "installment_types": InstallmentCategory.choices,
        "existing_emis": EMI.objects.filter(debit=debit).order_by("sequence_number"),
    })
