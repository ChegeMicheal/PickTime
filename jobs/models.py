from django.db import models
from django.utils import timezone

class Job(models.Model):
    title = models.CharField(max_length=200)
    short_description = models.TextField()
    poster = models.ImageField(upload_to='jobs/posters/', blank=True, null=True)
    description_file = models.FileField(upload_to='jobs/descriptions/', blank=True, null=True)
    apply_link = models.URLField(blank=True, null=True)

    closing_date = models.DateField(help_text="Job will disappear after this date")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['closing_date']

    def __str__(self):
        return self.title

    @property
    def is_open(self):
        return self.is_active and self.closing_date >= timezone.now().date()

    def days_remaining(self):
        return (self.closing_date - timezone.now().date()).days
