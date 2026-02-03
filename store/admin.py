from django.contrib import admin
from .models import Service, Event, EventPhoto, ContactSubmission
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.contrib import messages
from .models import ContactSubmission, ContactReply
from .forms import ContactReplyForm
from django.urls import path, reverse
from django.utils.html import format_html
from django import forms

# =========================
# SERVICES ADMIN
# =========================
class MiniServiceInline(admin.TabularInline):
    model = Service
    fk_name = 'parent'  # assuming you added parent FK
    extra = 1
    verbose_name = "Mini Service"
    verbose_name_plural = "Mini Services"
    

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["title", "parent", "is_active", "order"]
    list_filter = ["parent", "is_active"]
    search_fields = ["title", "short_description"]
    inlines = [MiniServiceInline]
    list_editable = ("is_active", "order")

    fieldsets = (
        ("Service Info", {
            "fields": ("title", "short_description", "image")
        }),
        ("Visibility & Order", {
            "fields": ("is_active", "order")
        }),
    )
    
    def get_queryset(self, request):
        """Hide mini-services from main list."""
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True)  # only top-level services    

# =========================
# EVENT PHOTOS INLINE
# =========================
class EventPhotoInline(admin.TabularInline):
    model = EventPhoto
    extra = 1


# =========================
# EVENTS ADMIN
# =========================
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "start_date",
        "end_date",
        "status_display",
        "featured",
        "rsvp_enabled",
    )
    list_filter = ("featured", "rsvp_enabled")
    search_fields = ("title",)

    inlines = [EventPhotoInline]

    fieldsets = (
        ("Event Info", {
            "fields": ("title", "description", "thumbnail")
        }),
        ("Schedule", {
            "fields": ("start_date", "end_date")
        }),
        ("Visibility & Actions", {
            "fields": ("featured", "rsvp_enabled")
        }),
    )

    def status_display(self, obj):
        return obj.get_status_display()

    status_display.short_description = "Status"

    class Media:
        css = {
            "all": ("admin/css/custom_admin.css",)
        }


# =========================
# EVENT PHOTOS (OPTIONAL SEPARATE VIEW)
# =========================
@admin.register(EventPhoto)
class EventPhotoAdmin(admin.ModelAdmin):
    list_display = ("event", "caption")
    search_fields = ("event__title",)

class ContactReplyForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 6, 'cols': 60}),
        label='Reply Message'
    )

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject', 'created_at', 'reply_link')
    readonly_fields = ('full_name', 'email', 'phone', 'subject', 'message', 'created_at')
    
    # Reply button in list
    def reply_link(self, obj):
        url = reverse('admin:contactsubmission-reply', args=[obj.pk])
        return format_html('<a class="button" href="{}">Reply</a>', url)
    reply_link.short_description = 'Reply'

    # Add custom admin URL
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'reply/<int:submission_id>/',
                self.admin_site.admin_view(self.reply_view),
                name='contactsubmission-reply'
            ),
        ]
        return custom_urls + urls

    # Reply view
    def reply_view(self, request, submission_id):
        submission = get_object_or_404(ContactSubmission, pk=submission_id)

        if request.method == 'POST':
            form = ContactReplyForm(request.POST)
            if form.is_valid():
                reply_msg = form.cleaned_data['message']

                # Send email to user
                send_mail(
                    subject=f"Reply to your message: {submission.subject}",
                    message=reply_msg,
                    from_email=None,  # default from_email in settings
                    recipient_list=[submission.email],
                )

                # Optional: mark as replied
                submission.status = 'replied'
                submission.save()

                self.message_user(request, "Reply sent successfully!")
                return redirect('admin:store_contactsubmission_changelist')
        else:
            form = ContactReplyForm(initial={
                'message': f"Hi {submission.full_name},\n\nRegards,\n\nPicktime Consulting (K) Ltd"  # prefill greeting
            })

        context = {
            'form': form,
            'submission': submission,
            'opts': self.model._meta,
            'title': f"Reply to {submission.full_name}"
        }

        return render(request, 'store/admin/contact_reply.html', context)

def change_view(self, request, object_id, form_url='', extra_context=None):
    if extra_context is None:
        extra_context = {}
    extra_context['reply_url'] = reverse('admin:contactsubmission-reply', args=[object_id])
    return super().change_view(request, object_id, form_url, extra_context=extra_context)


@admin.action(description="Mark selected messages as resolved")
def mark_resolved(self, request, queryset):
    queryset.update(status="resolved")

actions = [mark_resolved]

def client_portal(self, obj):
    return format_html(
        '<a href="/message/{}/" target="_blank">Open Client View</a>',
        obj.token
    )

class ContactReplyInline(admin.TabularInline):
    model = ContactReply
    extra = 0
    readonly_fields = ("body", "sent_at", "sent_by_admin")
    can_delete = False

class ContactReplyInline(admin.TabularInline):
    model = ContactReply
    extra = 0
    readonly_fields = ("body", "sent_at", "sent_by_admin")
    can_delete = False

def status_badge(self, obj):
    colors = {
        "new": "#dc3545",
        "replied": "#0d6efd",
        "resolved": "#198754",
    }
    return format_html(
        '<span style="color:white;padding:3px 8px;border-radius:12px;background:{}">{}</span>',
        colors[obj.status],
        obj.get_status_display(),
    )
    
    from django.contrib import admin
