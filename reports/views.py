from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from debit.models import Debit
from emi.models import EMI
from income.models import Income
from expense.models import Expense
import pandas as pd
from io import BytesIO
from django.template.loader import render_to_string
import pdfkit


@login_required
def entry_page(request):
    return render(request, 'reports/entry.html')

@login_required
def debit_report(request):
    user = request.user
    debits = Debit.objects.filter(user=user)

    # Filters
    debit_id = request.GET.get('debit_id','')
    lender_name = request.GET.get('lender_name','')
    emi_type = request.GET.get('emi_type','')
    status = request.GET.getlist('status')
    start_date_from = request.GET.get('start_date_from')
    start_date_to = request.GET.get('start_date_to')
    maturity_date_from = request.GET.get('maturity_date_from')
    maturity_date_to = request.GET.get('maturity_date_to')

    if debit_id:
        debits = debits.filter(debit_id__icontains=debit_id)
    if lender_name:
        debits = debits.filter(lender_name__icontains=lender_name)
    if emi_type:
        debits = debits.filter(emi_type=emi_type)
    if status:
        debits = debits.filter(status__in=status)
    if start_date_from:
        debits = debits.filter(start_date__gte=start_date_from)
    if start_date_to:
        debits = debits.filter(start_date__lte=start_date_to)
    if maturity_date_from:
        debits = debits.filter(maturity_date__gte=maturity_date_from)
    if maturity_date_to:
        debits = debits.filter(maturity_date__lte=maturity_date_to)

    # Sorting
    sort_field = request.GET.get('sort_field','debit_id')
    sort_order = request.GET.get('sort_order','asc')
    if sort_order == 'desc':
        sort_field = '-' + sort_field
    debits = debits.order_by(sort_field)
    selected_status = request.GET.getlist('status')  # list of selected status
    
    sort_fields = [
    ('debit_id','ID'),
    ('lender_name','Lender Name'),
    ('amount','Amount'),
    ('start_date','Start Date'),
    ('maturity_date','Maturity Date'),
]

    context = {
        'debits': debits,
        'status_choices': Debit._meta.get_field('status').choices,
        'emi_choices': Debit._meta.get_field('emi_type').choices,
        'selected_filters': request.GET,
        'selected_status': status,
        'sort_fields': sort_fields,
    }


    return render(request, 'reports/debit.html', context)


@login_required
def emi_report(request):
    user = request.user
    emis = EMI.objects.filter(user=user)

    # Filters
    emi_id = request.GET.get('emi_id','')
    debit_id = request.GET.get('debit_id','')
    status = request.GET.getlist('status')  # <- get list here
    due_from = request.GET.get('due_from')
    due_to = request.GET.get('due_to')
    paid_from = request.GET.get('paid_from')
    paid_to = request.GET.get('paid_to')

    if emi_id:
        emis = emis.filter(emi_id__icontains=emi_id)
    if debit_id:
        emis = emis.filter(debit__debit_id__icontains=debit_id)
    if status:
        emis = emis.filter(status__in=status)
    if due_from:
        emis = emis.filter(due_date__gte=due_from)
    if due_to:
        emis = emis.filter(due_date__lte=due_to)
    if paid_from:
        emis = emis.filter(paid_date__gte=paid_from)
    if paid_to:
        emis = emis.filter(paid_date__lte=paid_to)

    # Sorting
    sort_field = request.GET.get('sort_field','emi_id')
    sort_order = request.GET.get('sort_order','asc')
    if sort_order=='desc':
        sort_field = '-' + sort_field
    emis = emis.order_by(sort_field)

    context = {
        'emis': emis,
        'status_choices': EMI._meta.get_field('status').choices,
        'selected_filters': request.GET,
        'selected_status': status,  # <-- pass the list to template
        'sort_fields': [
            ('emi_id','EMI ID'),
            ('debit__debit_id','Debit ID'),
            ('amount','Amount'),
            ('due_date','Due Date'),
            ('paid_date','Paid Date'),
        ]
    }
    return render(request, 'reports/emi.html', context)
@login_required
def income_report(request):
    user = request.user
    incomes = Income.objects.filter(user=user)

    # Filters
    category = request.GET.getlist('category')
    source = request.GET.get('source','')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if category:
        incomes = incomes.filter(category__in=category)
    if source:
        incomes = incomes.filter(source__icontains=source)
    if date_from:
        incomes = incomes.filter(date__gte=date_from)
    if date_to:
        incomes = incomes.filter(date__lte=date_to)

    # Sorting
    sort_field = request.GET.get('sort_field','income_id')
    sort_order = request.GET.get('sort_order','asc')
    if sort_order=='desc':
        sort_field = '-' + sort_field
    incomes = incomes.order_by(sort_field)

    context = {
        'incomes': incomes,
        'category_choices': Income._meta.get_field('category').choices,
        'selected_filters': request.GET,
        'selected_categories': category,  # <-- pass this list to template
        'sort_fields': [
            ('income_id','Income ID'),
            ('category','Category'),
            ('source','Source'),
            ('amount','Amount'),
            ('date','Date')
        ],
    }
    return render(request, 'reports/income.html', context)
@login_required
def expense_report(request):
    user = request.user
    expenses = Expense.objects.filter(user=user)

    # Filters
    expense_id = request.GET.get('expense_id','')
    category = request.GET.getlist('category')
    title = request.GET.get('title','')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    if expense_id:
        expenses = expenses.filter(expense_id__icontains=expense_id)
    if category:
        expenses = expenses.filter(category__in=category)
    if title:
        expenses = expenses.filter(title__icontains=title)
    if date_from:
        expenses = expenses.filter(date__gte=date_from)
    if date_to:
        expenses = expenses.filter(date__lte=date_to)

    # Sorting
    sort_field = request.GET.get('sort_field','expense_id')
    sort_order = request.GET.get('sort_order','asc')
    if sort_order=='desc':
        sort_field = '-' + sort_field
    expenses = expenses.order_by(sort_field)

    context = {
        'expenses': expenses,
        'category_choices': Expense._meta.get_field('category').choices,
        'selected_filters': request.GET,
        'selected_categories': category,  # <-- pass list to template
        'sort_fields': [
            ('expense_id','Expense ID'),
            ('category','Category'),
            ('title','Title'),
            ('amount','Amount'),
            ('date','Date')
        ],
    }
    return render(request, 'reports/expense.html', context)

@login_required
def export_report(request, file_type, report_type):
    user = request.user
    filters = request.GET

    if report_type == 'debit':
        qs = Debit.objects.filter(user=user)
        # Apply debit filters
        debit_id = filters.get('debit_id','')
        lender_name = filters.get('lender_name','')
        emi_type = filters.get('emi_type','')
        status = filters.getlist('status')
        start_date_from = filters.get('start_date_from')
        start_date_to = filters.get('start_date_to')
        maturity_date_from = filters.get('maturity_date_from')
        maturity_date_to = filters.get('maturity_date_to')
        min_amount = filters.get('min_amount')
        max_amount = filters.get('max_amount')

        if debit_id: qs = qs.filter(debit_id__icontains=debit_id)
        if lender_name: qs = qs.filter(lender_name__icontains=lender_name)
        if emi_type: qs = qs.filter(emi_type=emi_type)
        if status: qs = qs.filter(status__in=status)
        if start_date_from: qs = qs.filter(start_date__gte=start_date_from)
        if start_date_to: qs = qs.filter(start_date__lte=start_date_to)
        if maturity_date_from: qs = qs.filter(maturity_date__gte=maturity_date_from)
        if maturity_date_to: qs = qs.filter(maturity_date__lte=maturity_date_to)
        if min_amount: qs = qs.filter(amount__gte=min_amount)
        if max_amount: qs = qs.filter(amount__lte=max_amount)

        columns = ['debit_id','lender_name','amount','interest_percent','start_date','maturity_date','is_emi','emi_type','emi_period','status']

    elif report_type == 'emi':
        qs = EMI.objects.filter(user=user)
        emi_id = filters.get('emi_id','')
        debit_id = filters.get('debit_id','')
        status = filters.getlist('status')
        due_from = filters.get('due_from')
        due_to = filters.get('due_to')
        paid_from = filters.get('paid_from')
        paid_to = filters.get('paid_to')

        if emi_id: qs = qs.filter(emi_id__icontains=emi_id)
        if debit_id: qs = qs.filter(debit__debit_id__icontains=debit_id)
        if status: qs = qs.filter(status__in=status)
        if due_from: qs = qs.filter(due_date__gte=due_from)
        if due_to: qs = qs.filter(due_date__lte=due_to)
        if paid_from: qs = qs.filter(paid_date__gte=paid_from)
        if paid_to: qs = qs.filter(paid_date__lte=paid_to)

        columns = ['emi_id','debit_id','amount','due_date','paid_date','status']

    elif report_type == 'income':
        qs = Income.objects.filter(user=user)
        category = filters.getlist('category')
        source = filters.get('source','')
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')

        if category: qs = qs.filter(category__in=category)
        if source: qs = qs.filter(source__icontains=source)
        if date_from: qs = qs.filter(date__gte=date_from)
        if date_to: qs = qs.filter(date__lte=date_to)

        columns = ['income_id','category','source','amount','date']

    elif report_type == 'expense':
        qs = Expense.objects.filter(user=user)
        expense_id = filters.get('expense_id','')
        category = filters.getlist('category')
        title = filters.get('title','')
        date_from = filters.get('date_from')
        date_to = filters.get('date_to')

        if expense_id: qs = qs.filter(expense_id__icontains=expense_id)
        if category: qs = qs.filter(category__in=category)
        if title: qs = qs.filter(title__icontains=title)
        if date_from: qs = qs.filter(date__gte=date_from)
        if date_to: qs = qs.filter(date__lte=date_to)

        columns = ['expense_id','category','title','amount','date']

    else:
        return HttpResponse("Invalid report type")

    # Sorting
    sort_field = filters.get('sort_field', columns[0])
    sort_order = filters.get('sort_order','asc')
    if sort_order == 'desc':
        sort_field = '-' + sort_field
    qs = qs.order_by(sort_field)

    # Convert to DataFrame
    data = []
    for obj in qs:
        row = []
        for col in columns:
            if col == 'debit_id' and hasattr(obj,'debit'):
                val = obj.debit.debit_id
            else:
                val = getattr(obj, col, '')
            if hasattr(val,'__str__'): val = str(val)
            row.append(val)
        data.append(row)

    df = pd.DataFrame(data, columns=columns)

    # Export
    if file_type == 'excel':
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={report_type}_report.xlsx'
        return response
    elif file_type == 'pdf':
        html_string = render_to_string('reports/pdf_template.html', {'columns': columns, 'data': data, 'report_type': report_type})
        pdf = pdfkit.from_string(html_string, False)
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={report_type}_report.pdf'
        return response
    else:
        return HttpResponse("Invalid file type")
