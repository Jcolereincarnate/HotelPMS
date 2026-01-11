# core/views.py
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, CustomUserCreationForm
from .decorators import role_required
from .models import CustomUser, Hotel
from rooms.models import Room
from guests.models  import Guest
from billing.models import Payment
from django.utils import timezone
from django.db.models import Sum, Case, When, IntegerField,Count
from datetime import timedelta
from datetime import datetime, timedelta

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('dashboard')
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')

@login_required(login_url='login')
#@role_required(['admin', 'manager', 'receptionist', 'accounting'])
def dashboard(request):
    rooms_count = Room.objects.count()
    occupied_count = Room.objects.filter(status='occupied').count()
    guests_count = Guest.objects.count()
    today = timezone.now().date()
    today_payments = Payment.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    start_date = today - timedelta(days=11)
    dates = [(start_date + timedelta(days=i)) for i in range(12)]
    revenue_labels = [d.strftime('%d %b') for d in dates]
    room_revenue = []
    service_revenue = []

    for date in dates:
        start = datetime.combine(date, datetime.min.time())
        end = datetime.combine(date, datetime.max.time())
        daily_total = Payment.objects.filter(
            created_at__range=(start, end),
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0
        room_revenue.append(float(daily_total)) 
        service_revenue.append(0)

    room_types_qs = (
    Room.objects
    .filter(status='occupied')
    .values('room_type__name')
    .annotate(count=Count('id'))
    .order_by('room_type__name')
)
    hotel = Hotel.objects.first()

    occupancy_labels = [r['room_type__name'] for r in room_types_qs]
    occupancy_data = [r['count'] for r in room_types_qs]

    context = {
        'title': 'Dashboard',
        'rooms_count': rooms_count,
        'occupied_count': occupied_count,
        'guests_count': guests_count,
        'today_payments': today_payments,
        'revenue_labels': revenue_labels,
        'room_revenue': room_revenue,
        'service_revenue': service_revenue,
        'occupancy_labels': occupancy_labels,
        'occupancy_data': occupancy_data,
        'hotel': hotel,
    }
    return render(request, 'core/dashboard.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def user_management(request):
    from .models import CustomUser
    users = CustomUser.objects.filter(is_active=True)
    context = {
        'title': 'User Management',
        'users': users,
    }
    return render(request, 'core/user_management.html', context)

@login_required(login_url='login')
@role_required(['admin'])
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('user_management')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'title': 'Create User',
        'form': form,
    }
    return render(request, 'core/create_user.html', context)

@login_required(login_url='login')
@role_required(['admin'])
def edit_user(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('user_management')
    else:
        form = CustomUserCreationForm(instance=user)
    
    context = {
        'title': 'Edit User',
        'form': form,
        'user_obj': user,
    }
    return render(request, 'core/edit_user.html', context)

@login_required(login_url='login')
@role_required(['admin'])
def delete_user(request, pk):
    user = get_object_or_404(CustomUser, id=pk)

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted successfully.')
        return redirect('user_management')
    
    context = {
        'title': 'Delete User',
        'user_obj': user,
    }
    return render(request, 'core/delete_user.html', context)