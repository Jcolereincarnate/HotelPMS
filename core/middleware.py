from django.shortcuts import redirect
from django.contrib import messages

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.role_permissions = {
            'admin': ['/', '/admin/'],
            'manager': ['/reservations/', '/guests/', '/rooms/', '/billing/', '/analytics/'],
            'receptionist': ['/reservations/', '/guests/', '/rooms/status/'],
            'housekeeping': ['/rooms/housekeeping/', '/rooms/tasks/'],
            'accounting': ['/billing/', '/analytics/'],
        }
    
    def __call__(self, request):
        response = self.get_response(request)
        return response