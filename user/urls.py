from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
   # path('', views.view_all_debits, name="view_all_debits"),
    path('add/', views.create_user, name="add_user"),
    path('', views.user_login, name="login"),
path('home/', views.home, name="home"),
        path('profile', views.profile, name="profile"),
    path("logout/", views.logout_view, name="logout"),

 path('change-password/', views.change_password, name='change_password'),
  path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('reset-password/', views.reset_password_view, name='reset_password'),
   #  path('forget-password/', views.forget_password, name='forget_password'),
   # path('debits/update/<str:pk>/', views.update_debit, name="update_debit"),
   # path('debits/delete/<str:pk>/', views.delete_debit, name="delete_debit"),
]
