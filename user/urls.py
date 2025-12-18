from django.urls import path
from . import views

urlpatterns = [
   # path('', views.view_all_debits, name="view_all_debits"),
    path('add/', views.create_user, name="add_user"),
    path('', views.user_login, name="login"),
    path('home', views.home, name="home"),
        path('profile', views.profile, name="profile"),

 path('change-password/', views.change_password, name='change_password'),
   #  path('forget-password/', views.forget_password, name='forget_password'),
   # path('debits/update/<str:pk>/', views.update_debit, name="update_debit"),
   # path('debits/delete/<str:pk>/', views.delete_debit, name="delete_debit"),
]
