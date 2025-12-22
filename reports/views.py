from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from debit.models import Debit
from emi.models import EMI
from income.models import Income
from expense.models import Expense
import pandas as pd
from io import BytesIO
from django.template.loader import render_to_string
import pdfkit
from decimal import Decimal
from datetime import datetime  # Add this import


@login_required
def entry_page(request):
    return render(request, 'reports/entry.html')


@login_required
def debit_report(request):
    user = request.user
    debits = Debit.objects.filter(user=user).order_by('-debit_id')

    # Get filter parameters
    filters = request.GET
    
    # Apply filters
    if filters.get('debit_id'):
        debits = debits.filter(debit_id__icontains=filters['debit_id'])
    if filters.get('lender_name'):
        debits = debits.filter(lender_name__icontains=filters['lender_name'])
    if filters.get('emi_type'):
        debits = debits.filter(emi_type=filters['emi_type'])
    if filters.getlist('status'):
        debits = debits.filter(status__in=filters.getlist('status'))
    if filters.get('start_date_from'):
        debits = debits.filter(start_date__gte=filters['start_date_from'])
    if filters.get('start_date_to'):
        debits = debits.filter(start_date__lte=filters['start_date_to'])
    if filters.get('maturity_date_from'):
        debits = debits.filter(maturity_date__gte=filters['maturity_date_from'])
    if filters.get('maturity_date_to'):
        debits = debits.filter(maturity_date__lte=filters['maturity_date_to'])
    if filters.get('min_amount'):
        try:
            debits = debits.filter(amount__gte=Decimal(filters['min_amount']))
        except:
            pass
    if filters.get('max_amount'):
        try:
            debits = debits.filter(amount__lte=Decimal(filters['max_amount']))
        except:
            pass

    # Sorting
    sort_field = filters.get('sort_field', '-debit_id')
    sort_order = filters.get('sort_order', 'asc')
    if sort_order == 'desc' and not sort_field.startswith('-'):
        sort_field = '-' + sort_field
    elif sort_order == 'asc' and sort_field.startswith('-'):
        sort_field = sort_field[1:]
    
    debits = debits.order_by(sort_field)

    # Pagination
    paginator = Paginator(debits, 50)  # Show 50 items per page
    page_number = request.GET.get('page')
    debits_page = paginator.get_page(page_number)

    # Get dropdown choices from model
    status_choices = Debit._meta.get_field('status').choices or []
    emi_choices = Debit._meta.get_field('emi_type').choices or []

    context = {
        'debits': debits_page,
        'status_choices': status_choices,
        'emi_choices': emi_choices,
        'selected_filters': dict(filters),
        'selected_status': filters.getlist('status', []),
        'sort_fields': [
            ('debit_id', 'ID'),
            ('lender_name', 'Lender Name'),
            ('amount', 'Amount'),
            ('start_date', 'Start Date'),
            ('maturity_date', 'Maturity Date'),
        ],
    }
    
    return render(request, 'reports/debit.html', context)


@login_required
def emi_report(request):
    user = request.user
    emis = EMI.objects.filter(user=user).select_related('debit').order_by('-emi_id')

    # Get filter parameters
    filters = request.GET
    
    # Apply filters
    if filters.get('emi_id'):
        emis = emis.filter(emi_id__icontains=filters['emi_id'])
    if filters.get('debit_id'):
        emis = emis.filter(debit__debit_id__icontains=filters['debit_id'])
    if filters.getlist('status'):
        emis = emis.filter(status__in=filters.getlist('status'))
    if filters.get('due_from'):
        emis = emis.filter(due_date__gte=filters['due_from'])
    if filters.get('due_to'):
        emis = emis.filter(due_date__lte=filters['due_to'])
    if filters.get('paid_from'):
        emis = emis.filter(paid_date__gte=filters['paid_from'])
    if filters.get('paid_to'):
        emis = emis.filter(paid_date__lte=filters['paid_to'])
    if filters.get('min_amount'):
        try:
            emis = emis.filter(amount__gte=Decimal(filters['min_amount']))
        except:
            pass
    if filters.get('max_amount'):
        try:
            emis = emis.filter(amount__lte=Decimal(filters['max_amount']))
        except:
            pass

    # Sorting
    sort_field = filters.get('sort_field', '-emi_id')
    sort_order = filters.get('sort_order', 'asc')
    if sort_order == 'desc' and not sort_field.startswith('-'):
        sort_field = '-' + sort_field
    elif sort_order == 'asc' and sort_field.startswith('-'):
        sort_field = sort_field[1:]
    
    emis = emis.order_by(sort_field)

    # Pagination
    paginator = Paginator(emis, 50)
    page_number = request.GET.get('page')
    emis_page = paginator.get_page(page_number)

    # Get dropdown choices from model
    status_choices = EMI._meta.get_field('status').choices or []

    context = {
        'emis': emis_page,
        'status_choices': status_choices,
        'selected_filters': dict(filters),
        'selected_status': filters.getlist('status', []),
        'sort_fields': [
            ('emi_id', 'EMI ID'),
            ('debit__debit_id', 'Debit ID'),
            ('amount', 'Amount'),
            ('due_date', 'Due Date'),
            ('paid_date', 'Paid Date'),
        ],
    }
    
    return render(request, 'reports/emi.html', context)


@login_required
def income_report(request):
    user = request.user
    incomes = Income.objects.filter(user=user).order_by('-income_id')

    # Get filter parameters
    filters = request.GET
    
    # Apply filters
    if filters.getlist('category'):
        incomes = incomes.filter(category__in=filters.getlist('category'))
    if filters.get('source'):
        incomes = incomes.filter(source__icontains=filters['source'])
    if filters.get('date_from'):
        incomes = incomes.filter(date__gte=filters['date_from'])
    if filters.get('date_to'):
        incomes = incomes.filter(date__lte=filters['date_to'])
    if filters.get('min_amount'):
        try:
            incomes = incomes.filter(amount__gte=Decimal(filters['min_amount']))
        except:
            pass
    if filters.get('max_amount'):
        try:
            incomes = incomes.filter(amount__lte=Decimal(filters['max_amount']))
        except:
            pass

    # Sorting
    sort_field = filters.get('sort_field', '-income_id')
    sort_order = filters.get('sort_order', 'asc')
    if sort_order == 'desc' and not sort_field.startswith('-'):
        sort_field = '-' + sort_field
    elif sort_order == 'asc' and sort_field.startswith('-'):
        sort_field = sort_field[1:]
    
    incomes = incomes.order_by(sort_field)

    # Pagination
    paginator = Paginator(incomes, 50)
    page_number = request.GET.get('page')
    incomes_page = paginator.get_page(page_number)

    # Get dropdown choices from model
    category_choices = Income._meta.get_field('category').choices or []

    context = {
        'incomes': incomes_page,
        'category_choices': category_choices,
        'selected_filters': dict(filters),
        'selected_categories': filters.getlist('category', []),
        'sort_fields': [
            ('income_id', 'Income ID'),
            ('category', 'Category'),
            ('source', 'Source'),
            ('amount', 'Amount'),
            ('date', 'Date'),
        ],
    }
    
    return render(request, 'reports/income.html', context)


@login_required
def expense_report(request):
    user = request.user
    expenses = Expense.objects.filter(user=user).order_by('-expense_id')

    # Get filter parameters
    filters = request.GET
    
    # Apply filters
    if filters.get('expense_id'):
        expenses = expenses.filter(expense_id__icontains=filters['expense_id'])
    if filters.getlist('category'):
        expenses = expenses.filter(category__in=filters.getlist('category'))
    if filters.get('title'):
        expenses = expenses.filter(title__icontains=filters['title'])
    if filters.get('paid_to'):
        expenses = expenses.filter(paid_to__icontains=filters['paid_to'])
    if filters.get('date_from'):
        expenses = expenses.filter(date__gte=filters['date_from'])
    if filters.get('date_to'):
        expenses = expenses.filter(date__lte=filters['date_to'])
    if filters.get('min_amount'):
        try:
            expenses = expenses.filter(amount__gte=Decimal(filters['min_amount']))
        except:
            pass
    if filters.get('max_amount'):
        try:
            expenses = expenses.filter(amount__lte=Decimal(filters['max_amount']))
        except:
            pass

    # Sorting
    sort_field = filters.get('sort_field', '-expense_id')
    sort_order = filters.get('sort_order', 'asc')
    if sort_order == 'desc' and not sort_field.startswith('-'):
        sort_field = '-' + sort_field
    elif sort_order == 'asc' and sort_field.startswith('-'):
        sort_field = sort_field[1:]
    
    expenses = expenses.order_by(sort_field)

    # Pagination
    paginator = Paginator(expenses, 50)
    page_number = request.GET.get('page')
    expenses_page = paginator.get_page(page_number)

    # Get dropdown choices from model
    category_choices = Expense._meta.get_field('category').choices or []

    context = {
        'expenses': expenses_page,
        'category_choices': category_choices,
        'selected_filters': dict(filters),
        'selected_categories': filters.getlist('category', []),
        'sort_fields': [
            ('expense_id', 'Expense ID'),
            ('title', 'Title'),
            ('category', 'Category'),
            ('amount', 'Amount'),
            ('date', 'Date'),
            ('paid_to', 'Paid To'),
        ],
    }
    
    return render(request, 'reports/expense.html', context)
@login_required
def export_report(request, file_type, report_type):
    user = request.user
    filters = request.GET

    if report_type == 'debit':
        qs = Debit.objects.filter(user=user)
        columns = ['debit_id', 'lender_name', 'amount', 'interest_percent', 
                  'start_date', 'maturity_date', 'is_emi', 'emi_type', 
                  'emi_period', 'status']
        amount_col_index = 2  # amount is at index 2
        
        # Apply filters
        if filters.get('debit_id'):
            qs = qs.filter(debit_id__icontains=filters['debit_id'])
        if filters.get('lender_name'):
            qs = qs.filter(lender_name__icontains=filters['lender_name'])
        if filters.get('emi_type'):
            qs = qs.filter(emi_type=filters['emi_type'])
        if filters.getlist('status'):
            qs = qs.filter(status__in=filters.getlist('status'))
        if filters.get('start_date_from'):
            qs = qs.filter(start_date__gte=filters['start_date_from'])
        if filters.get('start_date_to'):
            qs = qs.filter(start_date__lte=filters['start_date_to'])
        if filters.get('maturity_date_from'):
            qs = qs.filter(maturity_date__gte=filters['maturity_date_from'])
        if filters.get('maturity_date_to'):
            qs = qs.filter(maturity_date__lte=filters['maturity_date_to'])
        if filters.get('min_amount'):
            try:
                qs = qs.filter(amount__gte=Decimal(filters['min_amount']))
            except:
                pass
        if filters.get('max_amount'):
            try:
                qs = qs.filter(amount__lte=Decimal(filters['max_amount']))
            except:
                pass

    elif report_type == 'emi':
        qs = EMI.objects.filter(user=user).select_related('debit')
        columns = ['emi_id', 'debit_id', 'amount', 'due_date', 
                  'paid_date', 'status', 'penalty']
        amount_col_index = 2  # amount is at index 2
        
        # Apply filters
        if filters.get('emi_id'):
            qs = qs.filter(emi_id__icontains=filters['emi_id'])
        if filters.get('debit_id'):
            qs = qs.filter(debit__debit_id__icontains=filters['debit_id'])
        if filters.getlist('status'):
            qs = qs.filter(status__in=filters.getlist('status'))
        if filters.get('due_from'):
            qs = qs.filter(due_date__gte=filters['due_from'])
        if filters.get('due_to'):
            qs = qs.filter(due_date__lte=filters['due_to'])
        if filters.get('paid_from'):
            qs = qs.filter(paid_date__gte=filters['paid_from'])
        if filters.get('paid_to'):
            qs = qs.filter(paid_date__lte=filters['paid_to'])
        if filters.get('min_amount'):
            try:
                qs = qs.filter(amount__gte=Decimal(filters['min_amount']))
            except:
                pass
        if filters.get('max_amount'):
            try:
                qs = qs.filter(amount__lte=Decimal(filters['max_amount']))
            except:
                pass

    elif report_type == 'income':
        qs = Income.objects.filter(user=user)
        columns = ['income_id', 'category', 'source', 'amount', 
                  'date', 'description']
        amount_col_index = 3  # amount is at index 3
        
        # Apply filters
        if filters.getlist('category'):
            qs = qs.filter(category__in=filters.getlist('category'))
        if filters.get('source'):
            qs = qs.filter(source__icontains=filters['source'])
        if filters.get('date_from'):
            qs = qs.filter(date__gte=filters['date_from'])
        if filters.get('date_to'):
            qs = qs.filter(date__lte=filters['date_to'])
        if filters.get('min_amount'):
            try:
                qs = qs.filter(amount__gte=Decimal(filters['min_amount']))
            except:
                pass
        if filters.get('max_amount'):
            try:
                qs = qs.filter(amount__lte=Decimal(filters['max_amount']))
            except:
                pass

    elif report_type == 'expense':
        qs = Expense.objects.filter(user=user)
        columns = ['expense_id', 'category', 'title', 'amount', 
                  'date', 'paid_to', 'description']
        amount_col_index = 3  # amount is at index 3
        
        # Apply filters
        if filters.get('expense_id'):
            qs = qs.filter(expense_id__icontains=filters['expense_id'])
        if filters.getlist('category'):
            qs = qs.filter(category__in=filters.getlist('category'))
        if filters.get('title'):
            qs = qs.filter(title__icontains=filters['title'])
        if filters.get('paid_to'):
            qs = qs.filter(paid_to__icontains=filters['paid_to'])
        if filters.get('date_from'):
            qs = qs.filter(date__gte=filters['date_from'])
        if filters.get('date_to'):
            qs = qs.filter(date__lte=filters['date_to'])
        if filters.get('min_amount'):
            try:
                qs = qs.filter(amount__gte=Decimal(filters['min_amount']))
            except:
                pass
        if filters.get('max_amount'):
            try:
                qs = qs.filter(amount__lte=Decimal(filters['max_amount']))
            except:
                pass

    else:
        return HttpResponse("Invalid report type")

    # Sorting
    sort_field = filters.get('sort_field', columns[0])
    sort_order = filters.get('sort_order', 'asc')
    if sort_order == 'desc' and not sort_field.startswith('-'):
        sort_field = '-' + sort_field
    elif sort_order == 'asc' and sort_field.startswith('-'):
        sort_field = sort_field[1:]
    
    qs = qs.order_by(sort_field)

    # Prepare data
    data = []
    for obj in qs:
        row = []
        for col in columns:
            if col == 'debit_id' and hasattr(obj, 'debit'):
                val = obj.debit.debit_id if obj.debit else ''
            elif col == 'debit_id' and hasattr(obj, 'debit_id'):
                val = obj.debit_id
            elif col == 'penalty' and hasattr(obj, 'penalty'):
                val = obj.penalty if obj.penalty else '0.00'
            else:
                val = getattr(obj, col, '')
            
            # Format values
            if val is None:
                val = ''
            elif isinstance(val, bool):
                val = 'Yes' if val else 'No'
            elif hasattr(val, 'strftime'):
                val = val.strftime('%Y-%m-%d')
            elif isinstance(val, Decimal):
                val = f"{val:.2f}"
            
            row.append(str(val) if val else '')
        data.append(row)

    # Calculate total amount
    total_amount = 0
    for row in data:
        try:
            if row[amount_col_index]:  # Check if amount cell is not empty
                total_amount += float(row[amount_col_index])
        except (ValueError, TypeError, IndexError):
            continue

    # Get user's full name
    generated_by = f"{user.first_name} {user.last_name}".strip()
    if not generated_by:
        generated_by = user.username

    # Export
    if file_type == 'excel':
        df = pd.DataFrame(data, columns=columns)
        output = BytesIO()
        df.to_excel(output, index=False)
        output.seek(0)
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={report_type}_report.xlsx'
        return response
        
    elif file_type == 'pdf':
        context = {
            'columns': columns,
            'data': data,
            'report_type': report_type,
            'total_amount': f"{total_amount:.2f}",
            'amount_col_index': amount_col_index,
            'generated_by': generated_by,
            'filter_count': len([v for k, v in filters.items() if v and k not in ['sort_field', 'sort_order', 'page']])
        }
        
        html_string = render_to_string('reports/pdf_template.html', context)
        
        # Configure PDF options
        options = {
            'page-size': 'A4',
            'margin-top': '15mm',
            'margin-right': '15mm',
            'margin-bottom': '15mm',
            'margin-left': '15mm',
            'encoding': "UTF-8",
            'no-outline': None,
            'quiet': '',
            'enable-local-file-access': None
        }
        
        try:
            # First try with pdfkit
            pdf = pdfkit.from_string(html_string, False, options=options)
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename={report_type}_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            return response
        except Exception as e:
            # Fallback: return HTML for debugging or use alternative PDF generation
            return HttpResponse(f"""
                <h3>Error generating PDF</h3>
                <p>{str(e)}</p>
                <p>Please ensure wkhtmltopdf is installed on your system.</p>
                <p>For Ubuntu/Debian: sudo apt-get install wkhtmltopdf</p>
                <p>For CentOS/RHEL: sudo yum install wkhtmltopdf</p>
                <hr>
                <h4>Preview of HTML content:</h4>
                {html_string}
            """)
            
    else:
        return HttpResponse("Invalid file type")