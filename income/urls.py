from django.urls import path
from . import views

urlpatterns = [
    path('', views.view_all_income, name='view_all_income'),
    path('add',views.add_income,name="add_income"),
    path('delete/<str:pk>',views.delete_income,name="delete_income"),
    path('update/<str:pk>',views.income_update,name="update_income"),

]