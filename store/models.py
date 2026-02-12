from django.db import models
from django.urls import reverse
from django.utils.timezone import now
from django.utils.text import slugify


# =========================
# SERVICES
# =========================
class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, null=True)
    short_description = models.TextField(blank=True, null=True)  # <-- allow blank
    image = models.ImageField(upload_to="services/", blank=True, null=True)

    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="mini_services"
    )

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


# =========================
# EVENTS
# =========================
class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    thumbnail = models.ImageField(
        upload_to="events/thumbnails/",
        blank=True,
        null=True
    )

    # 🔽 NEW FILE FIELDS
    training_pdf = models.FileField(
        upload_to="events/training/",
        blank=True,
        null=True,
        help_text="Upload training materials (PDF)"
    )

    nomination_form = models.FileField(
        upload_to="events/nominations/",
        blank=True,
        null=True,
        help_text="Upload nomination form (PDF/DOC)"
    )

    # 🔽 NEW FIELDS
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Venue or location of the event"
    )

    cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Cost of attending the event (leave blank if free)"
    )

    category = models.ForeignKey(
        "Service",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="events",
        help_text="Category of the event (link to Service)"
    )

    featured = models.BooleanField(default=False)
    rsvp_enabled = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    # -------- STATUS LOGIC --------
    @property
    def is_future(self):
        return self.start_date > now().date()

    @property
    def is_past(self):
        return self.end_date < now().date()

    @property
    def is_ongoing(self):
        return self.start_date <= now().date() <= self.end_date

    @property
    def status(self):
        if self.is_future:
            return "future"
        if self.is_past:
            return "past"
        return "ongoing"

    def get_status_display(self):
        return self.status.capitalize()

    def get_absolute_url(self):
        return reverse("event_detail", args=[self.id])



# =========================
# EVENT PHOTOS
# =========================
class EventPhoto(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="photos"
    )
    image = models.ImageField(upload_to="events/photos/")
    caption = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Photo for {self.event.title}"


# =========================
# CONTACT FORM
# =========================
from .validators import validate_document_file
import uuid


class ContactSubmission(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=150, blank=True, null=True)
    service = models.CharField(max_length=150, blank=True, null=True)
    message = models.TextField()

    
    attachment = models.FileField(
        upload_to="contact_attachments/",
        validators=[validate_document_file],
        blank=True,
        null=True
    )


    submitted_at = models.DateTimeField(auto_now_add=True)

    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ("new", "New"),
            ("replied", "Replied"),
            ("resolved", "Resolved"),
        ],
        default="new"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.subject or 'No Subject'}"
    

# REPLY MODEL
# =========================
class ContactReply(models.Model):
    submission = models.ForeignKey(
        ContactSubmission,
        on_delete=models.CASCADE,
        related_name="replies"
    )

    body = models.TextField()
    sent_by_admin = models.BooleanField(default=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reply to {self.submission.email}"

