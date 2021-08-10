from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
# from .forms import UserRegistrationForm
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str, force_text, DjangoUnicodeDecodeError
from .utils import generate_token
UserModel = get_user_model()
from django.conf import settings
import threading
from django.urls import reverse


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()

def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_FROM_USER,
                         to=[user.email]
                         )
    EmailThread(email).start()

def resend_activation_email(request):
    user = User.object.all()
    print(user) 
    
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_FROM_USER,
                         to=[user.email]
                         )
    email.send()

def index(request):

    return render(request, 'sign.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        try:
            userid = User.objects.get(username=username)
            lookup= userid.is_active
        except Exception as e:
            lookup = True
        if not lookup:
            messages.error(request, "activate account by checking your mail or sign up again",
                           extra_tags='alert alert-warning alert-dismissible fade show')
            return render(request,'sign.html' )

        if user is not None:
            login(request, user)
            redirect_url = request.GET.get('next', 'vote:list')
            return redirect(redirect_url)
        else:
            messages.error(request, "Username Or Password is incorrect!!",
                           extra_tags='alert alert-warning alert-dismissible fade show')
            return render(request, 'sign.html')
    return render(request, 'sign.html')

def logout_user(request):
    logout(request)
    return redirect('account:login')

def create_user(request):
    if request.method == 'POST':
        check1 = False
        check2 = False
        check3 = False
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password')
        password2= request.POST.get('password2')
        if password1 != password2:
                check1 = True
                messages.error(request, 'Password doesn\'t matched',
                               extra_tags='alert alert-warning alert-dismissible fade show')
        if User.objects.filter(username=username).exists():
            check2 = True
            messages.error(request, 'Username already exists',
                            extra_tags='alert alert-warning alert-dismissible fade show')
            
            
        if User.objects.filter(email=email).exists():
            
            userid = User.objects.get(email=email)
            
            if userid.is_active:
                check3 = True
                messages.error(request, 'Email already registered',
                            extra_tags='alert alert-warning alert-dismissible fade show')
            else:
                user = User.objects.get(email=email)
                send_activation_email(user, request)
                messages.error(request, 'please check your email to activate your account',
                            extra_tags='alert alert-warning alert-dismissible fade show')
                return redirect('account:login')

               
        if check1 or check2 or check3:
            messages.error(
                request, "Registration Failed", extra_tags='alert alert-warning alert-dismissible fade show')
            return redirect('account:register')
        else:
            user = User.objects.create_user(
                username=username, password=password2, email=email)
            
            user.is_active = False
            user.save()
            send_activation_email(user, request)

            messages.error(request, 'please check your email to activate your account',
                            extra_tags='alert alert-warning alert-dismissible fade show')
            return redirect('account:login')

    return render(request, 'sign.html')

def activate_user(request, uidb64, token):

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

    except Exception as e:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.error(request, 'Email verified, you can now login',
                            extra_tags='alert alert-warning alert-dismissible fade show')
        trut = True
        return redirect('account:login')

    return render(request, 'activate-failed.html', {"user": user})

