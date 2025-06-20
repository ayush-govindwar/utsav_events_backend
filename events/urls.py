from django.urls import path
from . import views

urlpatterns = [
    path('submit-inquiry/', views.submit_event_inquiry, name='submit_event_inquiry'),
    path('health/', views.health_check, name='health_check'),
]