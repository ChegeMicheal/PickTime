from django.urls import path
from .views import job_list

app_name = 'jobs'   # ✅ THIS IS THE KEY LINE

urlpatterns = [
    path('', job_list, name='list'),
]
