# analytics/views.py
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum, Avg
from datetime import timedelta
from core.decorators import role_required
from reservations.models import Reservation
from rooms.models import Room
from billing.models import Payment, Folio
from guests.models import Guest
from .models import AIReport, DailyMetrics
from .utils import get_hotel_analytics_data, get_ai_recommendations,save_ai_report

@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def analytics_dashboard(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    total_guests = Guest.objects.count()
    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    total_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__gte=last_30_days
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    avg_revenue = total_revenue / 30 if total_revenue > 0 else 0
    total_reservations = Reservation.objects.filter(
        created_at__date__gte=last_30_days
    ).count()
    
    confirmed_reservations = Reservation.objects.filter(
        status='confirmed',
        check_in_date__gte=today
    ).count()
    
    # Guest metrics
    repeat_guests = Guest.objects.filter(total_stays__gt=1).count()
    vip_guests = Guest.objects.filter(vip=True).count()
    
    # Average daily metrics
    daily_metrics = DailyMetrics.objects.filter(
        date__gte=last_30_days
    ).aggregate(
        avg_occupancy=Avg('occupancy_rate'),
        avg_guests=Avg('guest_count'),
        total_revenue=Sum('total_revenue')
    )
    
    context = {
        'title': 'Analytics Dashboard',
        'total_guests': total_guests,
        'total_rooms': total_rooms,
        'occupied_rooms': occupied_rooms,
        'occupancy_rate': round(occupancy_rate, 2),
        'total_revenue': round(total_revenue, 2),
        'avg_revenue': round(avg_revenue, 2),
        'total_reservations': total_reservations,
        'confirmed_reservations': confirmed_reservations,
        'repeat_guests': repeat_guests,
        'vip_guests': vip_guests,
        'daily_metrics': daily_metrics,
    }
    return render(request, 'analytics/dashboard.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def occupancy_analytics(request):
    today = timezone.now().date()
    last_90_days = today - timedelta(days=90)

    daily_data = DailyMetrics.objects.filter(
        date__gte=last_90_days
    ).order_by('date').values('date', 'occupancy_rate', 'guest_count', 'total_revenue')
 
    current_period = DailyMetrics.objects.filter(
        date__gte=today - timedelta(days=30),
        date__lt=today
    ).aggregate(
        avg_occupancy=Avg('occupancy_rate'),
        avg_guests=Avg('guest_count')
    )
    
    previous_period = DailyMetrics.objects.filter(
        date__gte=today - timedelta(days=60),
        date__lt=today - timedelta(days=30)
    ).aggregate(
        avg_occupancy=Avg('occupancy_rate'),
        avg_guests=Avg('guest_count')
    )
    
    occupancy_trend = (
        current_period['avg_occupancy'] - previous_period['avg_occupancy']
    ) if current_period['avg_occupancy'] and previous_period['avg_occupancy'] else 0
    print("Occupancy Trend",round(occupancy_trend, 2))
    print("Previous period Occupancy Average", previous_period)
    print("Current period Occupancy Average", current_period)
    context = {
        'title': 'Occupancy Analytics',
        'daily_data': list(daily_data),
        'current_period': current_period,
        'previous_period': previous_period,
        'occupancy_trend': round(occupancy_trend, 2),
    }
    return render(request, 'analytics/occupancy.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def revenue_analytics(request):
    """Revenue analysis and forecasting"""
    today = timezone.now().date()
    last_90_days = today - timedelta(days=90)
    
    # Revenue by payment method
    revenue_by_method = Payment.objects.filter(
        status='completed',
        created_at__date__gte=last_90_days
    ).values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    # Daily revenue trend
    daily_revenue = DailyMetrics.objects.filter(
        date__gte=last_90_days
    ).order_by('date').values('date', 'total_revenue')
    
    # Calculate revenue metrics
    total_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__gte=last_90_days
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    avg_daily_revenue = DailyMetrics.objects.filter(
        date__gte=last_90_days
    ).aggregate(avg=Avg('total_revenue'))['avg'] or 0
    
    # Growth rate (last 30 vs previous 30)
    last_30_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__gte=today - timedelta(days=30)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    prev_30_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__gte=today - timedelta(days=60),
        created_at__date__lt=today - timedelta(days=30)
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    growth_rate = (
        ((last_30_revenue - prev_30_revenue) / prev_30_revenue * 100)
        if prev_30_revenue > 0 else 0
    )
    
    context = {
        'title': 'Revenue Analytics',
        'revenue_by_method': list(revenue_by_method),
        'daily_revenue': list(daily_revenue),
        'total_revenue': round(total_revenue, 2),
        'avg_daily_revenue': round(avg_daily_revenue, 2),
        'growth_rate': round(growth_rate, 2),
        'last_30_revenue': round(last_30_revenue, 2),
    }
    return render(request, 'analytics/revenue.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def guest_insights(request):
    today = timezone.now().date()
    total_guests = Guest.objects.count()
    new_guests = Guest.objects.filter(
        created_at__date__gte=today - timedelta(days=30)
    ).count()
    
    repeat_guests = Guest.objects.filter(total_stays__gt=1).count()
    vip_guests = Guest.objects.filter(vip=True).count()
    top_spenders = Guest.objects.order_by('-total_spent')[:10]

    gender_dist = Guest.objects.exclude(gender='').values('gender').annotate(
        count=Count('id')
    )
    
    # Nationality distribution
    top_nationalities = Guest.objects.exclude(nationality='').values('nationality').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    context = {
        'title': 'Guest Insights',
        'total_guests': total_guests,
        'new_guests': new_guests,
        'repeat_guests': repeat_guests,
        'vip_guests': vip_guests,
        'top_spenders': top_spenders,
        'gender_dist': list(gender_dist),
        'top_nationalities': list(top_nationalities),
    }
    return render(request, 'analytics/guest_insights.html', context)
'''
@login_required(login_url='login')
@role_required(['admin', 'manager'])
def ai_recommendations(request):
    analytics_data = get_hotel_analytics_data()
    recommendations = get_ai_recommendations(analytics_data)
    
    context = {
        'title': 'AI Recommendations',
        'recommendations': recommendations,
        'analytics_data': analytics_data,
    }
    
    return render(request, 'analytics/recommendations.html', context)
'''
@login_required(login_url='login')
@role_required(['admin', 'manager'])
def ai_recommendations(request):
    """
    Main view for AI-powered recommendations using Hugging Face
    Now saves reports to database
    """
    # Get analytics data
    analytics_data = get_hotel_analytics_data()
    
    # Get AI recommendations
    recommendations = get_ai_recommendations(analytics_data)
    
    # Save the AI report to database
    report = save_ai_report(
        report_type='recommendations',
        title=f'Smart Recommendations - {timezone.now().date()}',
        summary=f'Generated {len(recommendations)} actionable recommendations based on current hotel performance',
        data=analytics_data,  # Store the raw analytics data
        insights=[],  # Could add more detailed insights here
        recommendations=recommendations  # Store the recommendations
    )
    
    context = {
        'title': 'AI Recommendations',
        'recommendations': recommendations,
        'analytics_data': analytics_data,
        'report_id': report.id,  # Pass report ID to template
    }
    
    return render(request, 'analytics/recommendations.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def ai_report_history(request):
    reports = AIReport.objects.all()[:20]  # Last 20 reports
    
    context = {
        'title': 'AI Report History',
        'reports': reports,
    }
    return render(request, 'analytics/report_history.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def ai_report_detail(request, report_id):

    report = get_object_or_404(AIReport, id=report_id)
    
    context = {
        'title': f'AI Report - {report.created_at.date()}',
        'report': report,
    }
    return render(request, 'analytics/report_detail.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def performance_report(request):
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)

    revenue_30 = Payment.objects.filter(
        status='completed',
        created_at__date__gte=last_30_days
    ).aggregate(total=Sum('amount'))['total'] or 0

    reservations_30 = Reservation.objects.filter(
        created_at__date__gte=last_30_days
    ).count()
    
    completed_30 = Reservation.objects.filter(
        status='checked_out',
        checked_out_at__date__gte=last_30_days
    ).count()

    new_guests_30 = Guest.objects.filter(
        created_at__date__gte=last_30_days
    ).count()

    avg_occupancy = DailyMetrics.objects.filter(
        date__gte=last_30_days
    ).aggregate(avg=Avg('occupancy_rate'))['avg'] or 0
    
    context = {
        'title': 'Performance Report',
        'period': 'Last 30 Days',
        'revenue_30': round(revenue_30, 2),
        'reservations_30': reservations_30,
        'completed_30': completed_30,
        'new_guests_30': new_guests_30,
        'avg_occupancy': round(avg_occupancy, 2),
    }
    return render(request, 'analytics/performance_report.html', context)