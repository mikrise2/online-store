import logging

from django.contrib import messages
from django.contrib.auth import login, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.models import User

from store.forms import UserRegistrationForm, UserStandardLoginForm, ProfileForm, ProductForm
from store.models import Product
from store.tokens import account_activation_token

logger = logging.getLogger('logger')


def to_hash(product_id: int):
    return (product_id + 55691) * 55051


def from_hash(number: int):
    return (number // 55051) - 55691


def index(request):
    products = Product.objects.values()
    products = [entry for entry in products]
    for entry in products:
        entry['id'] = to_hash(entry['id'])
    context = {
        'products': products,
    }
    return render(request, 'index.html', context)


def product(request):
    return render(request, 'product.html')


# @login_required(redirect_field_name='', login_url='/login_failed')
# def create_product(request):
#     return render(request, 'create-product.html')


def profile(request, username):
    if request.method == 'POST':
        pass
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        return HttpResponseNotFound()
    return render(request, 'profile.html', {'profile': user})


def product_view(request, number):
    if request.method == 'POST':
        pass
    product_id = from_hash(number)
    product = Product.objects.filter(id=product_id).first()
    if product is None:
        return HttpResponseNotFound()
    return render(request, 'product.html', {'product': product})


def login_required_fail(request):
    messages.warning(request, 'You must be logged in to visit this page.')
    return redirect('/')


@login_required(redirect_field_name='', login_url='/login_failed')
def edit_profile(request):
    if request.method == 'POST':
        data = request.POST
        user = request.user
        if user.first_name != data['name']:
            user.first_name = data['name']
        if user.last_name != data['second-name']:
            user.last_name = data['second-name']
        user.save()
        messages.success(request, 'Information successfully changed')
        return redirect(f'/profile/{user.username}')
    return render(request, 'profile-edit.html')


@login_required(redirect_field_name='', login_url='/login_failed')
def my_products(request):
    products = Product.objects.filter(user_id=request.user.id).values()
    products = [entry for entry in products]
    for entry in products:
        entry['id'] = to_hash(entry['id'])
    context = {
        'products': products,
    }
    return render(request, 'my-products.html', context)


@login_required(redirect_field_name='', login_url='/login_failed')
def create_product(request):
    if request.method == 'POST':
        product_form = ProductForm(data=request.POST)
        if product_form.is_valid():
            product = product_form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, f'Product {product.name} has been successfully added')
        else:
            messages.error(request, 'Incorrect data has been entered for product')
        return redirect('/')
    return render(request, 'create-product.html')


@login_required(redirect_field_name='', login_url='/login_failed')
def edit_product(request, number):
    product_id = from_hash(number)
    product = Product.objects.get(pk=product_id)
    if product.user_id != request.user.id:
        messages.error(request, 'It isn\'t your product, you can\'t modify it.')
        return redirect('/')
    if request.method == 'GET':
        product.id = number
    if request.method == 'POST':
        product.update(request.POST)
        return redirect('/')
    context = {'product': product}
    return render(request, 'edit-product.html', context)


def registration(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(data=request.POST)
        profile_form = ProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.refresh_from_db()
            user.set_password(user.password)
            # user.is_active = False
            user.save()
            # activate_email(request, user, user_form.cleaned_data.get('email'))
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
        logger.error(f'Problem sending confirmation email to {to_email}')


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
            elif len(User.objects.filter(username=username)) > 0:
                logger.warning(f'user {username} is not active')
                messages.warning(request, 'You must activate your account. Please check your email.')
            else:
                logger.warning(f'no user {username}')
                messages.warning(request, f'No user with name {username} was found')
        else:
            logger.warning('input fields is not correct.')
    return redirect('/')


def activate(request, uidb64, token):
    user = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = user.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, user.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Thank you for your email confirmation. Now you can login your account.')
    else:
        messages.error(request, 'Activation link is invalid!')
        logger.error(f'failed activation: {token}, {request.path}')
    return redirect('/')
