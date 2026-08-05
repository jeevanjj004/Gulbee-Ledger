from django.shortcuts import render,get_object_or_404,redirect
from .models import EMI
from dateutil.relativedelta import relativedelta
from datetime import date
from debit.views import emi_id_fn
from debit.models import Debit
from collections import defaultdict

from django.db.models import Sum

from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.management import call_command

from django.views.decorators.csrf import csrf_exempt



@login_required
def view_emi(request):
    emis = EMI.objects.filter(
        debit__user=request.user
    ).select_related("debit").order_by("debit", "due_date")

    debit_data = defaultdict(lambda: {
        'debit': None,
        'emis': [],
        'overdue_count': 0,
        'pending_count': 0,
        'paid_count': 0,
        'status': 'paid'
    })

    for emi in emis:
        debit = emi.debit

        if debit_data[debit]['debit'] is None:
            debit_data[debit]['debit'] = debit

        debit_data[debit]['emis'].append(emi)

        if emi.status == "OVERDUE":
            debit_data[debit]['overdue_count'] += 1
            debit_data[debit]['status'] = 'overdue'

        elif emi.status == "PENDING":
            debit_data[debit]['pending_count'] += 1
            if debit_data[debit]['status'] != 'overdue':
                debit_data[debit]['status'] = 'pending'

        elif emi.status == "PAID":
            debit_data[debit]['paid_count'] += 1

    debit_groups = list(debit_data.values())

    return render(request, "view_all_emi.html", {
        "debit_groups": debit_groups,
    })


@login_required
def pay_emi(request, emi_id):
    emi = get_object_or_404(EMI, emi_id=emi_id)
    debit = emi.debit

    if request.method == "POST":
        # Process bill photo upload
        bill_photo = request.FILES.get('bill_photo')
        if bill_photo:
            emi.bill_photo = bill_photo
        # 1️⃣ Mark current EMI as PAID
        emi.status = "PAID"
        emi.paid_date = date.today()
        emi.save()

        # 2️⃣ Create next EMI only if pending installments exist
        if emi.sequence_number < debit.emi_period:
            next_seq = emi.sequence_number + 1

            # Calculate next due date
            if debit.installment_type == "MONTHLY":
                next_due_date = emi.due_date + relativedelta(months=1)
            else:
                next_due_date = emi.due_date + relativedelta(weeks=1)

            if next_seq == debit.emi_period:
                # LAST EMI
                next_amount = debit.last_emi_amount
            else:
                next_amount = debit.emi_amount

            EMI.objects.create(
                user=request.user,
                emi_id=emi_id_fn(),
                debit=debit,
                sequence_number=next_seq,
                amount=next_amount,
               
                due_date=next_due_date,
                status="PENDING"
            )

        # 3️⃣ If this was the LAST EMI → mark Debit COMPLETED
        if emi.sequence_number == debit.emi_period:
            debit.status = "COMPLETED"
            debit.save()

        return redirect("view_all_emi")

    return render(request, "pay_emi.html", {"emi": emi})
def emi_details(request, debit_id):
    debit = get_object_or_404(Debit, debit_id=debit_id)
    
    # Get existing payment records from DB to check if actually PAID
    recorded_emis = EMI.objects.filter(debit_id=debit_id).order_by('sequence_number')
    emi_map = {emi.sequence_number: emi for emi in recorded_emis}

    n_installment = debit.emi_period
    installment_type = debit.installment_type
    start_date = debit.start_date
    
    emi_rows = []
    current_due_date = start_date

    for seq in range(1, n_installment + 1):
        # 1. Calculate Date
        if installment_type == "MONTHLY":
            current_due_date += relativedelta(months=1)
        elif installment_type == "WEEKLY":
            current_due_date += relativedelta(weeks=1)

        # 2. Determine Amount (Use last_emi_amount for the final installment)
        if seq == n_installment:
            display_amount = debit.last_emi_amount
        else:
            display_amount = debit.emi_amount

        # 3. Check DB for actual status, else default to "PENDING"
        emi_obj = emi_map.get(seq)
        if emi_obj:
            current_status = emi_obj.status
            paid_date = emi_obj.paid_date
        else:
            current_status = "PENDING"
            paid_date = None

        emi_rows.append({
            "sequence": seq,
            "due_date": current_due_date,
            "amount": display_amount,
            "status": current_status,
            "paid_date": paid_date
        })

    # Count remaining based on the calculated list where status != PAID
    remaining_count = sum(1 for item in emi_rows if item['status'] != "PAID")

    context = {
        "debit": debit,
        "emi_rows": emi_rows,
        "remaining_emi": remaining_count,
    }
    return render(request, "emi_details.html", context)






@csrf_exempt
@require_POST
def run_emi_reminders(request):
    """
    -------------------------------------------------------------------------
    Internal EMI Reminder Trigger
    -------------------------------------------------------------------------

    Purpose
    -------
    This endpoint is designed ONLY for automated schedulers
    (e.g. cron-job.org).

    Instead of GitHub Actions running:

        python manage.py send_emi_reminders

    cron-job.org will make an HTTPS POST request to this endpoint.

    This endpoint then executes the existing Django management command.

    Why use this approach?
    ----------------------
    - No GitHub Actions required.
    - No Linux cron required.
    - Works on Render Free.
    - Reuses the already tested management command.
    - Keeps reminder logic in one place.

    Security
    --------
    This endpoint MUST NOT be publicly accessible.

    Every request must include the following HTTP header:

        X-CRON-TOKEN: <your_secret>

    The secret is stored in:

        settings.CRON_JOB_SECRET

    If the provided token does not match the configured secret,
    the request is rejected with HTTP 401 (Unauthorized).

    Example request

        POST /emi/internal/jobs/send-emi-reminders/

        Header:

            X-CRON-TOKEN: your-secret-token

    Response

        {
            "status": "success"
        }

    -------------------------------------------------------------------------
    """

    # Read the custom authentication header sent by cron-job.org
    token = request.headers.get("X-CRON-TOKEN")

    # Reject unauthorized requests
    if token != settings.CRON_JOB_SECRET:
        return JsonResponse(
            {
                "status": "error",
                "message": "Unauthorized",
            },
            status=401,
        )

    try:
        # Execute the existing management command.
        # This command contains all reminder logic,
        # email sending, and database updates.
        call_command("send_emi_reminders")

        return JsonResponse(
            {
                "status": "success",
                "message": "EMI reminders executed successfully.",
            }
        )

    except Exception as e:
        # Return the actual error for easier debugging.
        return JsonResponse(
            {
                "status": "error",
                "message": str(e),
            },
            status=500,
        )