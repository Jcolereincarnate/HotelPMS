from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Hotel
from billing.models import *
from analytics.models import *
from guests.models import *
from reservations.models import *
from rooms.models import *

admin.site.register(AIReport)
admin.site.register(DailyMetrics)
admin.site.register(Folio)
admin.site.register(FolioLineItem)
admin.site.register(Payment)
admin.site.register(PaystackTransaction)
admin.site.register(Guest)
admin.site.register(GuestContact)
admin.site.register(Reservation)
admin.site.register(ReservationAddon)
admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(HousekeepingTask)
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
        ('Contact', {'fields': ('phone',)}),
    )

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'currency')
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'address', 'phone', 'email')}),
        ('Settings', {'fields': ('currency', 'timezone', 'check_in_time', 'check_out_time')}),
    )