from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('users/', views.user_management, name='user_management'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<uuid:pk>/edit/', views.edit_user, name='edit_user'),
    path('users/<uuid:pk>/delete/', views.delete_user, name='delete_user'),
]