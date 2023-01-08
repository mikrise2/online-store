import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout

from store.forms import UserRegistrationForm, UserStandardLoginForm

logger = logging.getLogger("logger")


def index(request):
    return render(request, "index.html")


def registration(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
        else:
            logger.error(user_form.errors)
        return redirect('/')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})


def standard_login(request):
    if request.method == "POST":
        form = UserStandardLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                logger.warning(f'Invalid username or password. Username:{username}.')
        else:
            logger.warning(f'Fields input is not correct.')
    return redirect("/")


def logout_request(request):
    logout(request)
    return redirect("/")
