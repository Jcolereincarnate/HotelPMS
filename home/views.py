from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from reservations.forms import ReservationForm
from guests.forms import  GuestForm
from guests.models import Guest

# Home Page View
def home(request):
    return render(request, 'home/home.html')

# About Us Page View
def about(request):
    return render(request, 'home/about.html')


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        return JsonResponse({
            'status': 'success',
            'message': 'Thank you for contacting us. We will get back to you soon.'
        })
    
    return render(request, 'home/contact.html')


def reservation(request):
    if request.method == 'POST':
        gform = GuestForm(request.POST)
        rform = ReservationForm(request.POST)

        # Remove guest field ONLY for this page
        if 'guest' in rform.fields:
            rform.fields.pop('guest')

        if gform.is_valid() and rform.is_valid():
            # Create or get guest
            guest, created = Guest.objects.get_or_create(
                email=gform.cleaned_data['email'],
                defaults={
                    'first_name': gform.cleaned_data['first_name'],
                    'last_name': gform.cleaned_data['last_name'],
                    'phone': gform.cleaned_data['phone'],
                }
            )

            # Save reservation with total_price
            reservation = rform.save(commit=False)
            reservation.guest = guest

            # Calculate number of nights
            check_in = reservation.check_in_date
            check_out = reservation.check_out_date
            nights = (check_out - check_in).days
            if nights <= 0:
                nights = 1

            # Get room price_per_night
            room_price = reservation.room.price_per_night
            reservation.total_price = room_price * nights

            # Save reservation
            reservation.save()

            # Update room status to reserved
            room = reservation.room
            room.status = 'reserved'
            room.save()

            # Optional redirect
            # return redirect('reservation_success')

    else:
        gform = GuestForm()
        rform = ReservationForm()

        if 'guest' in rform.fields:
            rform.fields.pop('guest')

    context = {
        "gform": gform,
        "rform": rform
    }

    return render(request, 'home/reservation.html', context)