import logging

from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from store.forms import UserRegistrationForm, UserStandardLoginForm, ProfileForm
from store.models import Product
from store.tokens import account_activation_token

logger = logging.getLogger('logger')


def index(request):
    return render(request, 'index.html')


def product(request):
    return render(request, 'product.html')


def profile(request, username):  # TODO non existed accounts
    if request.method == 'POST':
        pass
    user = get_user_model().objects.filter(username=username).first()  # TODO DTO
    return render(request, 'profile.html', {'profile': user})


def login_required_fail(request):
    messages.warning(request, 'You must be logged in to visit this page.')
    return redirect('/')


@login_required(redirect_field_name='', login_url='/login_failed')  # TODO redirect_field_name
def edit_profile(request):
    return render(request, 'profile-edit.html')


def registration(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()
            user.profile.phone_number = profile_form.cleaned_data.get('phone_number')
            user.set_password(user.password)
            user.is_active = False
            user.save()
            activate_email(request, user, user_form.cleaned_data.get('email'))
        else:
            logger.error(user_form.errors)
        return redirect('/')
    else:
        user_form = UserRegistrationForm()
    return render(request, 'register.html', {'user_form': user_form})


def activate_email(request, user, to_email):
    mail_subject = 'Activate your user account.'
    message = render_to_string('template_activate_account.html', {
        'user': user.username,
        'domain': '127.0.0.1:8000',  # TODO
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(request, f'Dear {user}, please go to you email {to_email} inbox and click on \
               received activation link to confirm and complete the registration. Note: Check your spam folder.')
    else:
        messages.error(request, f'Problem sending confirmation email to {to_email}, check if you typed it correctly.')


def standard_login(request):
    if request.method == 'POST':
        form = UserStandardLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                logger.warning(f'Invalid username or password. Username:{username}.')
        else:
            logger.warning(f'Fields input is not correct.')
    return redirect('/')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
    else:
        messages.error(request, 'Activation link is invalid!')

    return redirect('/')
