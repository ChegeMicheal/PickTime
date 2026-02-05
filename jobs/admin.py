from django.contrib import admin
from django.utils import timezone
from .models import Job

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'closing_date', 'is_active', 'status')
    list_filter = ('is_active',)
    search_fields = ('title',)

    def status(self, obj):
        if obj.closing_date < timezone.now().date():
            return "❌ Closed"
        return "✅ Open"

    status.short_description = "Status"
