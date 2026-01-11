# billing/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.billing_dashboard, name='billing_dashboard'),
    path('folios/', views.folio_list, name='folio_list'),
    path('folios/<uuid:pk>/', views.folio_detail, name='folio_detail'),
    path('folios/<uuid:pk>/charge/', views.add_folio_charge, name='add_charge'),
    path('payment/<uuid:pk>/', views.record_payment, name='record_payment'),
    path('paystack/callback/', views.paystack_callback, name='paystack_callback'),
    path('reports/accounting/', views.accounting_report, name='accounting_report'),
    path('paystack/callback/', views.paystack_callback, name='paystack_callback'),
]