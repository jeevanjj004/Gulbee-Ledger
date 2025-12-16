from django.urls import path
from . import views

urlpatterns = [
    path('', views.entry_page, name='report_home'),  # Entry page
    path('debit/', views.debit_report, name='debit_report'),
    path('emi/', views.emi_report, name='emi_report'),
    path('income/', views.income_report, name='income_report'),
    path('expense/', views.expense_report, name='expense_report'),
    path('export/<str:file_type>/<str:report_type>/', views.export_report, name='export_report'),
]
