from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

from .forms import LoginForm, ForgotPasswordForm, SignupForm, ContactForm
from .models import Service, Event
from store.models import ContactSubmission


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
    services = Service.objects.filter(parent__isnull=True, is_active=True)
    
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
# store/views.py
def services(request):
    services = Service.objects.filter(parent__isnull=True, is_active=True)
    return render(request, 'store/services.html', {"services": services})


def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    mini_services = service.mini_services.all()  # Fetch all mini-services

    return render(request, "store/service_detail.html", {
        "service": service,
        "mini_services": mini_services
    })


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
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail, mail_admins

def contact(request):
    # Prefill from service/event buttons
    prefill_subject = request.GET.get('subject', '')
    prefill_service = request.GET.get('service', '')

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            submission = form.save()   # ✅ capture saved object
            
            from django.contrib import messages
            
            messages.success(
                request,
                "✅ Your message has been sent successfully. Keep checking your mail box We’ll get back to you shortly."
                )

            # -------------------------
            # Notify admins
            # -------------------------
            mail_admins(
                subject=f"New Contact Message: {submission.subject}",
                message=submission.message,
            )

            # -------------------------
            # Client portal link
            # -------------------------
            portal_link = request.build_absolute_uri(
                reverse("client_message_thread", args=[submission.token])
            )

            # -------------------------
            # Auto-reply to client
            # -------------------------
            send_mail(
                subject="We received your message",
                message=f"""
Hi {submission.full_name},

We’ve received your message and our team will respond shortly.

You can view replies and updates here:
{portal_link}

Regards,
Picktime Consulting
""",
                from_email=None,
                recipient_list=[submission.email],
            )

            return redirect('contact')  # or success page

    else:
        form = ContactForm(initial={
            'subject': prefill_subject,
            'service': prefill_service
        })

    return render(request, 'store/contact.html', {'form': form})


def client_message_thread(request, token):
    submission = get_object_or_404(ContactSubmission, token=token)

    return render(request, "store/client_thread.html", {
        "submission": submission
    })
    

# -------------------------
# CONTACT REPLY
# -------------------------
from .forms import ContactReplyForm

def contact_reply(request, submission_id):
    submission = get_object_or_404(ContactSubmission, id=submission_id)

    if request.method == "POST":
        form = ContactReplyForm(request.POST)
        if form.is_valid():
            reply_message = form.cleaned_data['message']

            # Send mail to user
            send_mail(
                subject=f"Re: {submission.subject}",
                message=f"Hi {submission.name},\n\n{reply_message}\n\nRegards,\nPicktime Consulting",
                from_email=None,  # uses DEFAULT_FROM_EMAIL
                recipient_list=[submission.email],
            )

            messages.success(request, f"Reply sent to {submission.name} ({submission.email})")
            return redirect('admin:store_contactsubmission_changelist')  # redirect to admin list
    else:
        form = ContactReplyForm(initial={
            'message': f"\n\n--- Original Message ---\n{submission.message}"
        })

    context = {
        'form': form,
        'submission': submission,
    }
    return render(request, 'store/admin/contact_reply.html', context)

