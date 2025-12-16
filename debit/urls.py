from django.urls import path
from . import views

urlpatterns = [
    path('add/', views.create_debit, name="add_debit"),
    path('delete/<str:pk>', views.delete_debit, name="delete"),
    path('update/<str:pk>', views.update_debit, name="update"),

    path('view_all/', views.view_all_debit, name="view_all"),

]
