from django.urls import path
from . import views

app_name = "account"

urlpatterns=[
    path('', views.login_user, name='index'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.create_user, name='register'),
    path('activate-user/<uidb64>/<token>',
         views.activate_user, name='activate'),
  
]
