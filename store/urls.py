from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('product', views.product, name='product'),
    path('login_failed', views.login_required_fail, name='login_failed'),
    path('profile/<username>', views.profile, name='profile'),
    path('edit-profile', views.edit_profile, name='edit-profile'),
    path('create-product', views.create_product, name='create-product'),
    path('registration', views.registration, name='registration'),
    path('login', views.standard_login, name='login'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
]
