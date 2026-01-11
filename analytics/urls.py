# analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('occupancy/', views.occupancy_analytics, name='occupancy_analytics'),
    path('revenue/', views.revenue_analytics, name='revenue_analytics'),
    path('guests/', views.guest_insights, name='guest_insights'),
    path('recommendations/', views.ai_recommendations, name='ai_recommendations'),
    path('reports/performance/', views.performance_report, name='performance_report'),
    path('recommendations/', views.ai_recommendations, name='ai_recommendations'),
    path('reports/', views.ai_report_history, name='ai_report_history'),
    path('reports/<uuid:report_id>/', views.ai_report_detail, name='ai_report_detail'),
]

