from django.contrib import admin
from .models import Service, Event, EventPhoto


# =========================
# SERVICES ADMIN
# =========================
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "is_active",
        "rsvp_enabled",
        "order",
        "created_at",
    )
    list_editable = (
        "is_active",
        "rsvp_enabled",
        "order",
    )
    search_fields = ("title",)
    ordering = ("order",)

    fieldsets = (
        ("Service Info", {
            "fields": ("title", "short_description", "description", "icon")
        }),
        ("Visibility & Actions", {
            "fields": ("is_active", "rsvp_enabled", "order")
        }),
    )

    class Media:
        css = {
            "all": ("admin/css/custom_admin.css",)
        }


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
