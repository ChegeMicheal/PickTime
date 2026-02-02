from django.db import models
from django.urls import reverse
from django.utils.timezone import now


# =========================
# SERVICES
# =========================
class Service(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    description = models.TextField(blank=True)

    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text="Optional icon class (e.g. fa-solid fa-briefcase)"
    )

    rsvp_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("service_detail", args=[self.id])


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
