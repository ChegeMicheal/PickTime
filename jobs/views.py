from django.shortcuts import render
from django.utils import timezone
from .models import Job

def job_list(request):
    today = timezone.now().date()

    jobs = Job.objects.filter(
        is_active=True,
        closing_date__gte=today
    )

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs
    })
