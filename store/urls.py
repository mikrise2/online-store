from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('registration', views.registration, name='registration'),
    path('login', views.standard_login, name='login'),
    path('logout', LogoutView.as_view(), name='logout')
]
