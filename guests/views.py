# guests/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from core.decorators import role_required
from .models import Guest, GuestContact
from .forms import GuestForm, GuestContactForm
from reservations.models import Reservation



@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def guest_list(request):
    search = request.GET.get('search', '')
    vip_filter = request.GET.get('vip', '')
    
    guests = Guest.objects.all().order_by('-created_at')
    
    if search:
        guests = guests.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    
    if vip_filter == 'true':
        guests = guests.filter(vip=True)
    
    context = {
        'title': 'Guest Management',
        'guests': guests,
        'search': search,
        'vip_filter': vip_filter,
    }
    return render(request, 'guests/guest_list.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def create_guest(request):
    if request.method == 'POST':
        form = GuestForm(request.POST)
        contact_form = GuestContactForm(request.POST)
        
        if form.is_valid():
            guest = form.save()
            
            if contact_form.is_valid():
                contact = contact_form.save(commit=False)
                contact.guest = guest
                contact.save()
            
            messages.success(request, f'Guest {guest.first_name} {guest.last_name} created successfully')
            return redirect('guest_detail', pk=guest.pk)
    else:
        form = GuestForm()
        contact_form = GuestContactForm()
    
    context = {
        'title': 'Create Guest',
        'form': form,
        'contact_form': contact_form,
    }
    return render(request, 'guests/create_guest.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def guest_detail(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    reservations = guest.reservations.all().order_by('-created_at')[:10]
    contact = guest.contact if hasattr(guest, 'contact') else None
    
    context = {
        'title': f'{guest.first_name} {guest.last_name}',
        'guest': guest,
        'reservations': reservations,
        'contact': contact,
    }
    return render(request, 'guests/guest_detail.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def edit_guest(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    contact = guest.contact if hasattr(guest, 'contact') else None
    
    if request.method == 'POST':
        form = GuestForm(request.POST, instance=guest)
        contact_form = GuestContactForm(request.POST, instance=contact) if contact else GuestContactForm(request.POST)
        
        if form.is_valid():
            guest = form.save()
            
            if contact_form.is_valid():
                contact_data = contact_form.save(commit=False)
                contact_data.guest = guest
                contact_data.save()
            
            messages.success(request, 'Guest information updated successfully')
            return redirect('guest_detail', pk=guest.pk)
    else:
        form = GuestForm(instance=guest)
        contact_form = GuestContactForm(instance=contact) if contact else GuestContactForm()
    
    context = {
        'title': f'Edit {guest.first_name}',
        'form': form,
        'contact_form': contact_form,
        'guest': guest,
    }
    return render(request, 'guests/edit_guest.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def guest_reservation_history(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    reservations = guest.reservations.all().order_by('-check_in_date')
    
    context = {
        'title': f'{guest.first_name} - Reservation History',
        'guest': guest,
        'reservations': reservations,
    }
    return render(request, 'guests/reservation_history.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def toggle_vip(request, pk):
    guest = get_object_or_404(Guest, pk=pk)
    guest.vip = not guest.vip
    guest.save()
    
    status = 'marked as VIP' if guest.vip else 'removed from VIP'
    messages.success(request, f'{guest.first_name} has been {status}')
    return redirect('guest_detail', pk=guest.pk)

@login_required(login_url='login')
@role_required(['admin', 'manager'])
def guest_analytics(request):
    total_guests = Guest.objects.count()
    vip_guests = Guest.objects.filter(vip=True).count()
    repeat_guests = Guest.objects.filter(total_stays__gt=1).count()
    
    top_spenders = Guest.objects.order_by('-total_spent')[:10]
    
    context = {
        'title': 'Guest Analytics',
        'total_guests': total_guests,
        'vip_guests': vip_guests,
        'repeat_guests': repeat_guests,
        'top_spenders': top_spenders,
    }
    return render(request, 'guests/analytics.html', context)

