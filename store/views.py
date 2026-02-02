from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

from .forms import LoginForm, ForgotPasswordForm, SignupForm
from .models import Service, Event

import random, string

# -------------------------
# SIGNUP
# -------------------------
def signup_view(request):
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')
    return render(request, 'store/signup.html', {'form': form})

# -------------------------
# LANDING PAGE
# -------------------------
def landing(request):
    services = Service.objects.filter(is_active=True).order_by("order")
    
    today = timezone.now().date()

    # Ongoing events: start_date <= today <= end_date
    ongoing_events = Event.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).order_by("start_date")

    # Upcoming events: start_date > today
    upcoming_events = Event.objects.filter(
        start_date__gt=today
    ).order_by("start_date")

    # Past events: end_date < today
    past_events = Event.objects.filter(
        end_date__lt=today
    ).order_by("-start_date")  # show most recent past first

    context = {
        "services": services,
        "ongoing_events": ongoing_events,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
    }

    return render(request, 'store/landing.html', context)


# -------------------------
# LOGIN
# -------------------------
def login_view(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('landing')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'store/login.html', {'form': form})

# -------------------------
# LOGOUT
# -------------------------
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('landing')

# -------------------------
# FORGOT PASSWORD
# -------------------------
def forgot_password(request):
    form = ForgotPasswordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)

            temp_password = ''.join(
                random.choices(string.ascii_letters + string.digits, k=8)
            )
            user.set_password(temp_password)
            user.save()

            send_mail(
                'TnT Password Reset',
                f'Hello {user.username},\n\n'
                f'Your temporary password is: {temp_password}\n'
                f'Please log in and change it immediately.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )

            messages.success(request, "Temporary password sent to your email.")
            return redirect('login')

        except User.DoesNotExist:
            messages.error(request, "No account found with that email.")

    return render(request, 'store/forgot_password.html', {'form': form})

# -------------------------
# SERVICES PAGE
# -------------------------
def services(request):
    services = Service.objects.filter(is_active=True).order_by("order")
    return render(request, 'store/services.html', {"services": services})

# -------------------------
# EVENTS PAGE
# -------------------------
def events_list(request):
    today = timezone.now().date()

    # Ongoing events: start_date <= today <= end_date
    ongoing_events = Event.objects.filter(
        start_date__lte=today,
        end_date__gte=today
    ).order_by("start_date")

    # Upcoming events: start_date > today
    upcoming_events = Event.objects.filter(
        start_date__gt=today
    ).order_by("start_date")

    # Past events: end_date < today
    past_events = Event.objects.filter(
        end_date__lt=today
    ).order_by("-start_date")  # show most recent past first

    context = {
        "services": services,
        "ongoing_events": ongoing_events,
        "upcoming_events": upcoming_events,
        "past_events": past_events,
    }
    return render(request, "store/events_list.html", context)


# -------------------------
# EVENT DETAIL PAGE
# -------------------------
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'store/event_detail.html', {"event": event})

# -------------------------
# SERVICE DETAIL PAGE
# -------------------------
def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'store/service_detail.html', {'service': service})

# -------------------------
# RSVP PAGES
# -------------------------
def rsvp_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, "store/rsvp.html", {"event": event})

def rsvp_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, "store/rsvp.html", {"service": service})

# -------------------------
# CONTACT PAGE
# -------------------------
def contact(request):
    return render(request, 'store/contact.html')

