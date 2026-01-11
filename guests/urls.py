# guests/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.guest_list, name='guest_list'),
    path('create/', views.create_guest, name='create_guest'),
    path('<uuid:pk>/', views.guest_detail, name='guest_detail'),
    path('<uuid:pk>/edit/', views.edit_guest, name='edit_guest'),
    path('<uuid:pk>/history/', views.guest_reservation_history, name='guest_history'),
    path('<uuid:pk>/vip/', views.toggle_vip, name='toggle_vip'),
    path('analytics/overview/', views.guest_analytics, name='guest_analytics'),
]