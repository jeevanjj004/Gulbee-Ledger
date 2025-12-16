from django.urls import path
from . import views


urlpatterns = [
    path('', views.view_all_expense, name="view_all_expense"),
    path('add/', views.add_expense, name="add_expense"),
    path('update/<str:pk>/', views.update_expense, name="update_expense"),
    path('delete/<str:pk>/', views.delete_expense, name="delete_expense"),
]
