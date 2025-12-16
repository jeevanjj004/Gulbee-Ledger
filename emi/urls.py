from django.urls import path
from . import views


urlpatterns = [
    path('', views.view_emi, name="view_all_emi"),
    path('pay_emi/<str:emi_id>', views.pay_emi, name="pay_emi"),
    path('emi_details/<str:debit_id>/', views.emi_details, name="emi_details"),
    # path('delete/<str:pk>/', views.delete_expense, name="delete_expense"),
]
