# rooms/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('create/', views.create_room, name='create_room'),
    path('<uuid:pk>/', views.room_detail, name='room_detail'),
    path('<uuid:pk>/edit/', views.edit_room, name='edit_room'),
    path('<uuid:pk>/delete/', views.delete_room, name='delete_room'),
    path('<uuid:pk>/status/', views.change_room_status, name='change_room_status'),
    path('housekeeping/', views.housekeeping_dashboard, name='housekeeping_tasks'),
    path('housekeeping/task/create/', views.create_housekeeping_task, name='create_task'),
    path('housekeeping/task/<uuid:pk>/', views.housekeeping_task_detail, name='task_detail'),
    path('occupancy/report/', views.room_occupancy_report, name='occupancy_report'),
    path('create_room_type/', views.create_room_type, name='create_room_type'), 
    path('<uuid:pk>/edit_task/', views.edit_housekeeping_task, name='edit_task'),
    path('<uuid:pk>/delete_task/', views.delete_housekeeping_task, name='delete_task'),
    path('<uuid:pk>/update_task/', views.update_housekeeping_task, name='update_task'),

]
