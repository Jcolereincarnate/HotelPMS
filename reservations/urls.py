# reservations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_list, name='reservation_list'),
    path('create/', views.create_reservation, name='create_reservation'),
    path('<uuid:pk>/', views.reservation_detail, name='reservation_detail'),
    path('<uuid:pk>/check-in/', views.check_in, name='check_in'),
    path('<uuid:pk>/check-out/', views.check_out, name='check_out'),
    path('<uuid:pk>/cancel/', views.cancel_reservation, name='cancel_reservation'),
    path('arrivals/today/', views.daily_arrivals, name='daily_arrivals'),
    path('departures/today/', views.daily_departures, name='daily_departures'),
    path('initiate-payment/<uuid:pk>/', views.initiate_checkin_payment, name='initiate_checkin_payment'),
]