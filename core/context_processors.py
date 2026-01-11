from .models import Hotel

def hotel_context(request):
    try:
        hotel = Hotel.objects.first()
    except:
        hotel = None
    
    return {
        'hotel': hotel,
    }