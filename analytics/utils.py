from openai import OpenAI
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from datetime import timedelta
from rooms.models import Room, HousekeepingTask
from reservations.models import Reservation
from billing.models import Payment, Folio
from .models import DailyMetrics, AIReport
import json,ast,re,requests
def get_hotel_analytics_data():
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)

    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    maintenance_rooms = Room.objects.filter(status='maintenance').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    total_reservations = Reservation.objects.filter(
        created_at__date__gte=last_30_days
    ).count()
    
    confirmed_reservations = Reservation.objects.filter(
        status='confirmed',
        check_in_date__gte=today
    ).count()
    
    upcoming_checkins = Reservation.objects.filter(
        status='confirmed',
        check_in_date__lte=today + timedelta(days=7),
        check_in_date__gte=today
    ).count()
    
    cancellation_rate = Reservation.objects.filter(
        created_at__date__gte=last_30_days,
        status='cancelled'
    ).count()
    cancellation_percentage = (cancellation_rate / total_reservations * 100) if total_reservations > 0 else 0
    
    monthly_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__gte=last_30_days
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    weekly_revenue = Payment.objects.filter(
        status='completed',
        created_at__date__gte=last_7_days
    ).aggregate(total=Sum('amount'))['total'] or 0

    completed_folios = Folio.objects.filter(
        status='settled',
        created_at__date__gte=last_30_days
    )
    
    if completed_folios.exists():
        avg_daily_rate = completed_folios.aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
    else:
        avg_daily_rate = 0
    
    pending_payments = Payment.objects.filter(status='pending').count()
    failed_payments = Payment.objects.filter(
        status='failed',
        created_at__date__gte=last_7_days
    ).count()

    outstanding_balance = Folio.objects.filter(
        status__in=['open', 'partial']
    ).aggregate(total=Sum('balance'))['total'] or 0

    pending_tasks = HousekeepingTask.objects.filter(
        status__in=['pending', 'in_progress']
    ).count()
    
    overdue_tasks = HousekeepingTask.objects.filter(
        status='pending',
        created_at__date__lt=today - timedelta(days=1)
    ).count()

    vip_upcoming = Reservation.objects.filter(
        guest__vip=True,
        status='confirmed',
        check_in_date__lte=today + timedelta(days=14),
        check_in_date__gte=today
    ).count()
    
    repeat_guests = Reservation.objects.filter(
        created_at__date__gte=last_30_days
    ).values('guest').annotate(
        visit_count=Count('id')
    ).filter(visit_count__gt=1).count()

    room_type_bookings = Reservation.objects.filter(
        created_at__date__gte=last_30_days,
        status__in=['confirmed', 'checked_in', 'checked_out']
    ).values('room__room_type__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return {
        'occupancy': {
            'rate': round(occupancy_rate, 2),
            'occupied': occupied_rooms,
            'total': total_rooms,
            'maintenance': maintenance_rooms
        },
        'reservations': {
            'total_monthly': total_reservations,
            'confirmed': confirmed_reservations,
            'upcoming_7days': upcoming_checkins,
            'cancellation_rate': round(cancellation_percentage, 2)
        },
        'revenue': {
            'monthly': float(monthly_revenue),
            'weekly': float(weekly_revenue),
            'average_daily_rate': float(avg_daily_rate),
            'outstanding_balance': float(outstanding_balance)
        },
        'payments': {
            'pending': pending_payments,
            'failed_recent': failed_payments
        },
        'housekeeping': {
            'pending': pending_tasks,
            'overdue': overdue_tasks
        },
        'guests': {
            'vip_upcoming': vip_upcoming,
            'repeat_guests': repeat_guests
        },
        'room_types': list(room_type_bookings)
    }
def get_ai_recommendations(analytics_data):
    try:
        API_URL = "https://router.huggingface.co/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_TOKEN}",
        }

        prompt = f"""
        You are a hotel management expert. Analyze this data and provide 5-7 actionable recommendations.

        HOTEL PERFORMANCE DATA:
        - Occupancy: {analytics_data['occupancy']['rate']}% ({analytics_data['occupancy']['occupied']}/{analytics_data['occupancy']['total']} rooms)
        - Maintenance Rooms: {analytics_data['occupancy']['maintenance']}
        - Monthly Reservations: {analytics_data['reservations']['total_monthly']}
        - Confirmed Reservations: {analytics_data['reservations']['confirmed']}
        - Upcoming Check-ins (7 days): {analytics_data['reservations']['upcoming_7days']}
        - Cancellation Rate: {analytics_data['reservations']['cancellation_rate']}%
        - Monthly Revenue: ₦{analytics_data['revenue']['monthly']:,.0f}
        - Weekly Revenue: ₦{analytics_data['revenue']['weekly']:,.0f}
        - Average Daily Rate: ₦{analytics_data['revenue']['average_daily_rate']:,.0f}
        - Pending Payments: {analytics_data['payments']['pending']}
        - Failed Payments: {analytics_data['payments']['failed_recent']}
        - Outstanding Balance: ₦{analytics_data['revenue']['outstanding_balance']:,.0f}
        - Pending Housekeeping: {analytics_data['housekeeping']['pending']}
        - Overdue Tasks: {analytics_data['housekeeping']['overdue']}
        - VIP Guests Coming: {analytics_data['guests']['vip_upcoming']}
        - Repeat Guests: {analytics_data['guests']['repeat_guests']}

        Provide recommendations as a JSON array with this exact format:
        [
        {{
            "title": "recommendation title",
            "message": "detailed 2-3 sentence explanation",
            "priority": "high",
            "type": "warning",
            "action": "Action Button Text"
        }}
        ]

        Focus on: revenue optimization, operational efficiency, guest experience, risk mitigation, and cost management.
        Return ONLY the JSON array, no other text.
        """

        payload = {
            "model": "meta-llama/Llama-3.2-3B-Instruct:novita",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 1200,
            "temperature": 0.7,
            "top_p": 0.95
        }

        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            generated_text = result["choices"][0]["message"]["content"]
            recommendations = parse_recommendations_from_text(generated_text)

            if recommendations and len(recommendations) > 0:
                return recommendations
            else:
                print("AI response parsing failed, using fallback recommendations")
                return get_fallback_recommendations(analytics_data)

        else:
            print(f"Hugging Face API Error: {response.status_code} - {response.text}")
            return get_fallback_recommendations(analytics_data)

    except Exception as e:
        print(f"Hugging Face API Error: {str(e)}")
        return get_fallback_recommendations(analytics_data)   
def parse_recommendations_from_text(text):
    if not text:
        return None
    text_clean = re.sub(r"```(?:json)?\s*", "", text)
    text_clean = re.sub(r"\s*```$", "", text_clean)
    text_clean = text_clean.strip()
    
    if text_clean.lower().startswith("json:"):
        text_clean = text_clean[5:].strip()

    try:
        first_idx = text_clean.index('[')
        last_idx = text_clean.rindex(']')
        candidate = text_clean[first_idx:last_idx + 1]
    except ValueError:
        candidate = text_clean 
        
    parse_attempts = [
        lambda s: json.loads(s),
        lambda s: ast.literal_eval(s), 
    ]

    for attempt in parse_attempts:
        try:
            parsed = attempt(candidate)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass

    array_matches = re.findall(r"\[[\s\S]*?\]", text_clean)
    for match in array_matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            try:
                parsed = ast.literal_eval(match)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                continue
    return None
def get_fallback_recommendations(analytics_data):
    recommendations = []
    occupancy_rate = analytics_data['occupancy']['rate']
    if occupancy_rate < 50:
        recommendations.append({
            'type': 'warning',
            'title': 'Low Occupancy Alert',
            'message': f'Current occupancy is {occupancy_rate}%. Consider launching promotional campaigns, offering discounts, or partnering with travel agencies to boost bookings.',
            'action': 'Launch Promotion',
            'priority': 'high'
        })
    elif occupancy_rate > 85:
        recommendations.append({
            'type': 'success',
            'title': 'High Demand Period',
            'message': f'Occupancy rate is {occupancy_rate}%. This is an excellent time to implement dynamic pricing and increase rates. Consider upselling premium room types.',
            'action': 'Adjust Pricing',
            'priority': 'medium'
        })
    elif 60 <= occupancy_rate <= 75:
        recommendations.append({
            'type': 'info',
            'title': 'Optimal Occupancy Range',
            'message': f'Occupancy at {occupancy_rate}% is healthy. Focus on maintaining service quality and guest satisfaction to encourage repeat bookings.',
            'priority': 'low'
        })
    if analytics_data['reservations']['upcoming_7days'] < 5:
        recommendations.append({
            'type': 'warning',
            'title': 'Low Upcoming Bookings',
            'message': f'Only {analytics_data["reservations"]["upcoming_7days"]} check-ins scheduled for the next week. Review marketing channels and consider flash sales or last-minute deals.',
            'action': 'Review Marketing',
            'priority': 'high'
        })
    elif analytics_data['reservations']['upcoming_7days'] > 20:
        recommendations.append({
            'type': 'info',
            'title': 'Busy Week Ahead',
            'message': f'{analytics_data["reservations"]["upcoming_7days"]} check-ins in the next 7 days. Ensure adequate staffing and prepare rooms in advance.',
            'action': 'Schedule Staff',
            'priority': 'medium'
        })

    if analytics_data['reservations']['cancellation_rate'] > 15:
        recommendations.append({
            'type': 'warning',
            'title': 'High Cancellation Rate',
            'message': f'Cancellation rate is {analytics_data["reservations"]["cancellation_rate"]}%. Review cancellation policies, implement stricter deposit requirements, or offer flexible rebooking options.',
            'action': 'Review Policy',
            'priority': 'medium'
        })
    if analytics_data['payments']['pending'] > 5:
        recommendations.append({
            'type': 'warning',
            'title': 'Payment Collection Required',
            'message': f'{analytics_data["payments"]["pending"]} payments are pending. Implement automated payment reminders and follow-up procedures to improve cash flow.',
            'action': 'Send Reminders',
            'priority': 'high'
        })
    
    if analytics_data['payments']['failed_recent'] > 3:
        recommendations.append({
            'type': 'warning',
            'title': 'Payment Failures',
            'message': f'{analytics_data["payments"]["failed_recent"]} failed payments in the last week. Review payment gateway settings and contact affected guests to resolve issues.',
            'action': 'Contact Guests',
            'priority': 'high'
        })
    if analytics_data['revenue']['weekly'] > 0 and analytics_data['revenue']['monthly'] > 0:
        weekly_avg = analytics_data['revenue']['weekly'] / 7
        monthly_avg = analytics_data['revenue']['monthly'] / 30
        if weekly_avg > monthly_avg * 1.2:
            recommendations.append({
                'type': 'success',
                'title': 'Revenue Trending Up',
                'message': f'Recent weekly revenue (₦{analytics_data["revenue"]["weekly"]:,.0f}) shows improvement. Maintain current strategies and consider expanding successful promotions.',
                'priority': 'low'
            })
    if analytics_data['housekeeping']['overdue'] > 5:
        recommendations.append({
            'type': 'warning',
            'title': 'Housekeeping Backlog',
            'message': f'{analytics_data["housekeeping"]["overdue"]} overdue housekeeping tasks. Consider reallocating staff or hiring temporary help to clear the backlog and maintain room availability.',
            'action': 'Review Staffing',
            'priority': 'medium'
        })
    elif analytics_data['housekeeping']['pending'] > 15:
        recommendations.append({
            'type': 'info',
            'title': 'High Housekeeping Volume',
            'message': f'{analytics_data["housekeeping"]["pending"]} pending tasks. Monitor workload and consider preventive scheduling to avoid delays.',
            'priority': 'low'
        })
    if analytics_data['guests']['vip_upcoming'] > 0:
        recommendations.append({
            'type': 'info',
            'title': 'VIP Guest Preparation',
            'message': f'{analytics_data["guests"]["vip_upcoming"]} VIP guest(s) arriving soon. Ensure premium amenities, welcome packages, and room upgrades are prepared. Assign experienced staff.',
            'action': 'Prepare VIP Welcome',
            'priority': 'medium'
        })
    if analytics_data['guests']['repeat_guests'] > 10:
        recommendations.append({
            'type': 'success',
            'title': 'Strong Guest Loyalty',
            'message': f'{analytics_data["guests"]["repeat_guests"]} repeat guests this month. Consider implementing a formal loyalty program with rewards to maintain this positive trend.',
            'action': 'Create Loyalty Program',
            'priority': 'low'
        })
    if analytics_data['revenue']['outstanding_balance'] > 50000:
        recommendations.append({
            'type': 'warning',
            'title': 'High Outstanding Balance',
            'message': f'₦{analytics_data["revenue"]["outstanding_balance"]:,.0f} in outstanding balances. Implement stricter payment policies and follow-up procedures to improve collections.',
            'action': 'Review Collections',
            'priority': 'high'
        })
    if analytics_data['occupancy']['maintenance'] > 3:
        recommendations.append({
            'type': 'warning',
            'title': 'Multiple Rooms Under Maintenance',
            'message': f'{analytics_data["occupancy"]["maintenance"]} rooms currently under maintenance. Expedite repairs to maximize revenue potential, especially during high-demand periods.',
            'action': 'Expedite Repairs',
            'priority': 'medium'
        })
    
    return recommendations
def update_daily_metrics(target_date=None):
    if target_date is None:
        target_date = timezone.now().date()

    total_rooms = Room.objects.count()
    occupied_rooms = Room.objects.filter(status='occupied').count()
    available_rooms = Room.objects.filter(status='available').count()
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0

    daily_revenue = Payment.objects.filter(
        status='completed',
        created_at__date=target_date
    ).aggregate(total=Sum('amount'))['total'] or 0

    check_ins = Reservation.objects.filter(
        checked_in_at__date=target_date
    ).count()
    
    # Get check-outs for the day
    check_outs = Reservation.objects.filter(
        checked_out_at__date=target_date
    ).count()
    
    # Get cancellations for the day
    cancellations = Reservation.objects.filter(
        status='cancelled',
        updated_at__date=target_date
    ).count()
    
    # Get guest count (currently checked in)
    guest_count = Reservation.objects.filter(
        status='checked_in',
        checked_in_at__date__lte=target_date
    ).count()
    
    # Update or create the daily metrics
    metrics, created = DailyMetrics.objects.update_or_create(
        date=target_date,
        defaults={
            'total_rooms': total_rooms,
            'occupied_rooms': occupied_rooms,
            'available_rooms': available_rooms,
            'occupancy_rate': round(occupancy_rate, 2),
            'total_revenue': daily_revenue,
            'guest_count': guest_count,
            'check_ins': check_ins,
            'check_outs': check_outs,
            'cancellations': cancellations,
        }
    )
    
    return metrics
def save_ai_report(report_type, title, summary, data, insights, recommendations):
    report = AIReport.objects.create(
        report_type=report_type,
        title=title,
        summary=summary,
        data=data,
        insights=insights,
        recommendations=recommendations
    )
    return report