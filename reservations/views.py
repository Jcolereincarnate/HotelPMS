# reservations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import timedelta
from core.decorators import role_required
from .models import Reservation, ReservationAddon
from .forms import ReservationForm, CheckInForm, CheckOutForm
from rooms.models import Room
from billing.models import Folio,FolioLineItem, Payment
from analytics.utils import update_daily_metrics

from .utils import send_notification


@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def reservation_list(request):
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    reservations = Reservation.objects.select_related('guest', 'room').order_by('-created_at')
    
    if status_filter:
        reservations = reservations.filter(status=status_filter)
    
    if search:
        reservations = reservations.filter(
            Q(guest__first_name__icontains=search) |
            Q(guest__last_name__icontains=search) |
            Q(guest__email__icontains=search) |
            Q(room__room_number__icontains=search)
        )
    
    context = {
        'title': 'Reservations',
        'reservations': reservations,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Reservation.STATUS_CHOICES,
    }
    return render(request, 'reservations/reservation_list.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def create_reservation(request):
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.created_by = request.user
            check_in = form.cleaned_data['check_in_date']
            check_out = form.cleaned_data['check_out_date']
            nights = (check_out - check_in).days
            room_price = form.cleaned_data['room'].price_per_night
            reservation.total_price = room_price * nights
            guest = reservation.number_of_guests
            room_max = reservation.room.room_type.max_occupancy
            if guest > room_max:
                 messages.warning(request, f'Max Occupancy Reached, Current listed guests is {guest}. This room can hold {room_max}, consider other Room Types ')
                 return redirect('create_reservation')
            reservation.save()
            room = reservation.room
            room.status ="reserved"
            room.save()
            messages.success(request, f'Reservation created successfully for {reservation.guest.first_name}')
            try:
                subject = f"Rerservation Created Successfully"
                message = f"""
                Hello {reservation.guest.first_name} {reservation.guest.last_name},

                Reservation details:
                Room Number: {reservation.room.room_number}
                Check in Date: {reservation.check_in_date}
                Check out Date: {reservation.check_out_date} at 12:00pm

                If you need to make any changes or have questions about your booking, please contact the front desk.

                Thank you for choosing our hotel. We look forward to hosting you.
                """
           
                send_notification(subject, message, receiver=reservation.guest.email)
            except:
                print("cannot send email")

        
    else:
        form = ReservationForm()
    
    context = {
        'title': 'Create Reservation',
        'form': form,
    }
    return render(request, 'reservations/create_reservation.html', context)


@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def reservation_detail(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    context = {
        'title': f'Reservation #{reservation.id}',
        'reservation': reservation,
    }
    return render(request, 'reservations/reservation_detail.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def check_in(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.status != 'confirmed':
        messages.error(request, 'Only confirmed reservations can be checked in.')
        return redirect('reservation_detail', pk=pk)
    try:
        folio = Folio.objects.get(reservation=reservation)
    except Folio.DoesNotExist:
        folio = Folio.objects.create(
            guest=reservation.guest,
            reservation=reservation,
            room_charges=reservation.room.price_per_night,
            total_amount=reservation.total_price,
            balance=reservation.total_price,
            status='open'
        )
        messages.info(request, 'Folio created. Please proceed with payment.')
    if folio.status == 'open' and folio.balance > 0:
        messages.warning(request, f'Payment required: ₦{folio.balance}. Please settle the folio before check-in.')
        return redirect('folio_detail', pk=folio.pk)
    
    if folio.status not in ['settled', 'partial']:
        messages.warning(request, 'Payment is required before check-in.')
        return redirect('folio_detail', pk=folio.pk)
    
    if request.method == 'POST':
        form = CheckInForm(request.POST)
        if form.is_valid():
            reservation.status = 'checked_in'
            reservation.checked_in_at = timezone.now()
            reservation.save()
            
            reservation.room.status = 'occupied'
            reservation.room.save()

            update_daily_metrics()
            
            messages.success(
                request, 
                f'{reservation.guest.first_name} checked in to room {reservation.room.room_number}'
            )
            return redirect('reservation_detail', pk=pk)
    else:
        form = CheckInForm()
    
    context = {
        'form': form,
        'reservation': reservation,
        'folio': folio
    }
    
    subject = f"Check In Successful – Reservation {reservation.id}"
    message = f"""Hello {reservation.guest.first_name} {reservation.guest.last_name},
    You have been successfully checked into {reservation.room.room_number} with reservation ID { reservation.id }.
    Your reservation details are as follows:
    Check-In Date: {reservation.checked_in_at}
    Check-Out Date: {reservation.check_out_date} at 12:00pm
    If you wish to extend the duration of your stay, please contact the front desk.
    We wish you a comfortable and enjoyable stay."""
    try:
        send_notification(subject, message, receiver=reservation.guest.email)
    except:
        print("cannot send email")
    return render(request, 'reservations/check_in.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def initiate_checkin_payment(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    if reservation.status != 'confirmed':
        messages.error(request, 'Only confirmed reservations can proceed to payment.')
        return redirect('reservation_detail', pk=pk)

    folio, created = Folio.objects.get_or_create(
        reservation=reservation,
        defaults={
            'guest': reservation.guest,
            'room_charges': reservation.room.price_per_night,
            'total_amount': reservation.total_price,
            'balance': reservation.total_price,
            'status': 'open'
        }
    )
    
    if created:
        messages.info(request, 'Folio created for this reservation.')

    messages.info(request, 'Please complete payment to proceed with check-in.')
    return redirect('folio_detail', pk=folio.pk)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def check_out(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    
    if reservation.status != 'checked_in':
        messages.error(request, 'Only checked-in reservations can be checked out.')
        return redirect('reservation_detail', pk=pk)
    
    if request.method == 'POST':
        form = CheckOutForm(request.POST)
        if form.is_valid():
            reservation.status = 'checked_out'
            reservation.checked_out_at = timezone.now()
            reservation.save()
            
            reservation.room.status = 'cleaning'
            reservation.room.save()
            
            update_daily_metrics()
            
            messages.success(
                request, 
                f'{reservation.guest.first_name} checked out from room {reservation.room.room_number}'
            )
            try:
                subject = f"Check In Successful – Reservation {reservation.id}"
                message = f"""
                Hello {reservation.guest.first_name} {reservation.guest.last_name},

                Your check out for room {reservation.room.room_number} with reservation ID {reservation.id} has been completed successfully.

                Your stay details are as follows:
                Check in Date: {reservation.checked_in_at}
                Check out Date: {reservation.check_out_date} at 12:00pm

                Thank you for staying with us. We hope you had a pleasant experience.
                If you have any feedback or wish to book your next stay, please contact the front desk.

                Safe travels, and we look forward to hosting you again.
                """
                send_notification(subject, message, receiver=reservation.guest.email)
            except:
                print("cannot send email")
            return redirect('reservation_detail', pk=reservation.pk)
    else:
        form = CheckOutForm()
    
    context = {
        'title': 'Check Out',
        'form': form,
        'reservation': reservation,
    }
    
    return render(request, 'reservations/check_out.html', context)


@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if request.method == 'POST':
        if reservation.status not in ['checked_in', 'checked_out']:
            reservation.status = 'cancelled'
            reservation.save()
            
            if reservation.room.status == 'occupied' or reservation.room.status=='reserved':
                reservation.room.status = 'available'
                reservation.room.save()
            update_daily_metrics()
            
            messages.success(request, 'Reservation cancelled successfully')
        else:
            messages.error(request, 'Cannot cancel checked-in or checked-out reservations.')
        
        return redirect('reservation_list')
    
    return redirect('reservation_detail', pk=pk)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def daily_arrivals(request):
    today = timezone.now().date()
    arrivals = Reservation.objects.filter(
        check_in_date=today,
        status='confirmed'
    ).select_related('guest', 'room')
    
    context = {
        'title': "Today's Arrivals",
        'reservations': arrivals,
        'date': today,
    }
    return render(request, 'reservations/daily_arrivals.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'receptionist'])
def daily_departures(request):
    today = timezone.now().date()
    departures = Reservation.objects.filter(
        check_out_date=today,
        status='checked_in'
    ).select_related('guest', 'room')
    
    context = {
        'title': "Today's Departures",
        'reservations': departures,
        'date': today,
    }
    return render(request, 'reservations/daily_departures.html', context)


    
    
