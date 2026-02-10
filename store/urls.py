from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    # Events
    path('events/', views.events_list, name='events_list'),
    path('events/<int:event_id>/', views.event_detail, name='event_detail'),
    path('events/<int:event_id>/rsvp/', views.rsvp_event, name='rsvp_event'),

    # Services
    path('services/', views.services, name='services'),
    path('services/<int:service_id>/', views.service_detail, name='service_detail'),
    path('services/<int:service_id>/rsvp/', views.rsvp_service, name='rsvp_service'),

    # Contact
    path('contact/', views.contact, name='contact'),
    path(
    "message/<uuid:token>/",
    views.client_message_thread,
    name="client_message_thread"
),
    path('admin/contact-reply/<int:submission_id>/', views.contact_reply, name='contact_reply'),

    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('signup/', views.signup_view, name='signup'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

