# billing/views.py
import requests
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.db.models import Sum, Q
from decimal import Decimal
from core.decorators import role_required
from reservations.models import ReservationAddon
from .models import Folio, Payment, FolioLineItem, PaystackTransaction
from .forms import FolioForm, PaymentForm, FolioLineItemForm
from django.urls import reverse
from analytics.utils import update_daily_metrics
from .utils  import update_folio_totals 
from guests.models import Guest

@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def billing_dashboard(request):
    today = timezone.now().date()
    today_payments = Payment.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    open_folios = Folio.objects.filter(status='open').count()
    partial_folios = Folio.objects.filter(status='partial').count()
    settled_today = Payment.objects.filter(
        created_at__date=today,
        status='completed'
    ).count()

    recent_payments = Payment.objects.select_related('folio__guest').order_by('-created_at')[:10]
    
    context = {
        'title': 'Billing Dashboard',
        'today_revenue': today_payments,
        'open_folios': open_folios,
        'partial_folios': partial_folios,
        'settled_today': settled_today,
        'recent_payments': recent_payments,
    }
    return render(request, 'billing/dashboard.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def folio_list(request):
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    folios = Folio.objects.select_related('guest', 'reservation').order_by('-created_at')
    
    if status_filter:
        folios = folios.filter(status=status_filter)
    
    if search:
        folios = folios.filter(
            Q(guest__first_name__icontains=search) |
            Q(guest__last_name__icontains=search) |
            Q(guest__email__icontains=search)
        )
    
    context = {
        'title': 'Folios & Billing',
        'folios': folios,
        'status_filter': status_filter,
        'search': search,
        'status_choices': Folio.STATUS_CHOICES,
    }
    return render(request, 'billing/folio_list.html', context)

@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def folio_detail(request, pk):
    folio = get_object_or_404(Folio, pk=pk)
    line_items = folio.line_items.all()
    payments = folio.payments.all().order_by('-created_at')
    
    context = {
        'title': f'Folio #{folio.id}',
        'folio': folio,
        'line_items': line_items,
        'payments': payments,
    }
    return render(request, 'billing/folio_detail.html', context)



@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def add_folio_charge(request, pk):
    folio = get_object_or_404(Folio, pk=pk)
    if request.method == 'POST':
        form = FolioLineItemForm(request.POST)
        if form.is_valid():
            line_item = form.save(commit=False)
            line_item.folio = folio
            print(folio.balance)
            line_item.total = line_item.amount * line_item.quantity
            line_item.save()
            update_folio_totals(folio)
            ReservationAddon.objects.create(reservation=folio.reservation, name=line_item.description, price=line_item.amount, quantity=line_item.quantity)
            messages.success(request, 'Charge added to folio')
            return redirect('folio_detail', pk=pk)
    else:
        form = FolioLineItemForm()
    
    context = {
        'title': 'Add Charge',
        'form': form,
        'folio': folio,
    }
    return render(request, 'billing/add_charge.html', context)
'''
@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def record_payment(request, pk):
    folio = get_object_or_404(Folio, pk=pk)
    folio_line_item = filter(folio=folio)
    price = int(folio.balance)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.folio = folio
            payment.recorded_by = request.user
            payment.transaction_ref = f"PMS-{uuid.uuid4().hex[:8].upper()}"
            
            if form.cleaned_data['payment_method'] == 'paystack':
                payment.save()
                return initiate_paystack_payment(request, payment, folio)
            else:
                payment.status = 'completed'
                payment.save()
                guest = folio.guest
                guest.total_spent += form.cleaned_data["amount"]
                guest.total_stays += 1
                guest.save()
                if guest.total_spent >= 100000:
                    guest.vip = True
                    guest.save()

                folio.amount_paid = (folio.amount_paid or 0) + payment.amount
                folio.balance = folio.total_amount - folio.amount_paid
                
                if folio.balance <= 0:
                    folio.status = 'settled'
                else:
                    folio.status = 'partial'
                folio.save()
                update_daily_metrics()
                
                messages.success(request, f'Payment of ₦{payment.amount} recorded successfully')
                return redirect('folio_detail', pk=pk)
    else:
        form = PaymentForm(initial={'amount': price})
    context = {
        'title': 'Record Payment',
        'form': form,
        'folio': folio,
    }
    return render(request, 'billing/record_payment.html', context)
'''
@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def record_payment(request, pk):
    folio = get_object_or_404(Folio, pk=pk)
    price = folio.balance or 0

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.folio = folio
            payment.recorded_by = request.user
            payment.transaction_ref = f"PMS-{uuid.uuid4().hex[:8].upper()}"

            if form.cleaned_data['payment_method'] == 'paystack':
                payment.save()
                return initiate_paystack_payment(request, payment, folio)
            else:
                payment.status = 'completed'
                payment.save()
                guest = folio.guest
                guest.total_spent += payment.amount
                guest.total_stays += 1
                guest.save()
                if guest.total_spent >= 100000:
                    guest.vip = True
                    guest.save()
                folio.amount_paid = (folio.amount_paid or 0) + payment.amount
                folio.balance-=folio.amount_paid
                remaining_payment = payment.amount
                unpaid_items = folio.line_items.filter(status='unpaid').order_by('created_at')

                for item in unpaid_items:
                    if remaining_payment >= item.total:
                        item.status = 'paid'
                        item.save()
                        remaining_payment -= item.total
                    else:
                        break
                update_folio_totals(folio)
                if folio.balance <= 0:
                    folio.status = 'settled'
                else:
                    folio.status = 'partial'
                folio.save()
                update_daily_metrics()
                
               
                messages.success(request, f'Payment of ₦{payment.amount} recorded successfully')
                return redirect('folio_detail', pk=pk)

    else:
        form = PaymentForm(initial={'amount': price})

    context = {
        'title': 'Record Payment',
        'form': form,
        'folio': folio,
    }
    return render(request, 'billing/record_payment.html', context)

def initiate_paystack_payment(request, payment, folio):
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY

    headers = {
        'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        'email': folio.guest.email,
        'amount': int(payment.amount * 100),
        'reference': payment.transaction_ref,
        'callback_url': request.build_absolute_uri(reverse('paystack_callback')),
    }

    try:
        response = requests.post(
            'https://api.paystack.co/transaction/initialize',
            json=payload,
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            
            PaystackTransaction.objects.create(
                payment=payment,
                authorization_url=data['data']['authorization_url'],
                access_code=data['data']['access_code'],
                paystack_reference=data['data']['reference'],
                amount=payment.amount,
                status='pending'
            )
            
            payment.status = 'pending'
            payment.save()
            context = {
                'folio': folio,
                'payment': payment,
                'authorization_url': data['data']['authorization_url'],
            }
            return render(request, 'billing/confirm_paystack.html', context)

        else:
            messages.error(request, 'Failed to initiate Paystack payment. Please try again.')
            return redirect('record_payment', pk=folio.pk)
    
    except requests.RequestException as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('record_payment', pk=folio.pk)
@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def paystack_callback(request):
    """Handle Paystack callback"""
    reference = request.GET.get('reference')
    PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
    
    headers = {
        'Authorization': f'Bearer {PAYSTACK_SECRET_KEY}',
    }
    
    try:
        response = requests.get(
            f'https://api.paystack.co/transaction/verify/{reference}',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['data']['status'] == 'success':
                # Update PaystackTransaction
                paystack_txn = PaystackTransaction.objects.get(paystack_reference=reference)
                paystack_txn.status = 'success'
                paystack_txn.paid_at = timezone.now()
                paystack_txn.save()
                
                # Update Payment
                payment = paystack_txn.payment
                payment.status = 'completed'
                payment.save()
                
                # Update Folio
                folio = payment.folio
                folio.amount_paid = (folio.amount_paid or 0) + payment.amount
                folio.balance = folio.total_amount - folio.amount_paid
                
                if folio.balance <= 0:
                    folio.status = 'settled'
                else:
                    folio.status = 'partial'
                
                folio.save()
                
                messages.success(request, f'Payment of ₦{payment.amount} completed successfully')
                return redirect('folio_detail', pk=folio.pk)
            else:
                paystack_txn = PaystackTransaction.objects.get(paystack_reference=reference)
                paystack_txn.status = 'failed'
                paystack_txn.save()
                
                payment = paystack_txn.payment
                payment.status = 'failed'
                payment.save()
                
                messages.error('Payment failed. Please try again.')
                return redirect('folio_detail', pk=payment.folio.pk)
    
    except Exception as e:
        messages.error(f'Error processing payment: {str(e)}')
        return redirect('billing_dashboard')



def paystack_callback(request):
    reference = request.GET.get('reference')
    
    if not reference:
        messages.error(request, "No transaction reference found.")
        return redirect('dashboard')

    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    response = requests.get(url, headers=headers)
    data = response.json()

    if data["status"] and data["data"]["status"] == "success":
        try:
            txn = PaystackTransaction.objects.get(paystack_reference=reference)
            payment = txn.payment
            folio = payment.folio

            txn.status = "completed"
            txn.save()

            payment.status = "completed"
            payment.save()

            folio.amount_paid = (folio.amount_paid or 0) + payment.amount
            folio.balance = folio.total_amount - folio.amount_paid
            folio.status = "settled" if folio.balance <= 0 else "partial"
            folio.save()
            
            # UPDATE DAILY METRICS AFTER SUCCESSFUL PAYMENT
            update_daily_metrics()

            messages.success(request, f"Payment of ₦{payment.amount} was successful.")
            return redirect('folio_detail', pk=folio.pk)
        except PaystackTransaction.DoesNotExist:
            messages.error(request, "Transaction not found in system.")
            return redirect('dashboard')
    else:
        messages.error(request, "Payment verification failed or cancelled.")
        return redirect('dashboard')

@login_required(login_url='login')
@role_required(['admin', 'manager', 'accounting'])
def accounting_report(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date and end_date:
        payments = Payment.objects.filter(
            status='completed',
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).order_by('payment_method')
    else:
        payments = list(
            Payment.objects.filter(status='completed')
            .order_by('payment_method')[:30]
        )

    # Compute totals
    cash_total = sum(p.amount for p in payments if p.payment_method == 'cash')
    card_total = sum(p.amount for p in payments if p.payment_method == 'card')
    bank_total = sum(p.amount for p in payments if p.payment_method == 'bank_transfer')
    paystack_total = sum(p.amount for p in payments if p.payment_method == 'paystack')
    
    total_revenue = cash_total + card_total + bank_total + paystack_total
    
    context = {
        'title': 'Accounting Report',
        'payments': payments,
        'cash_total': cash_total,
        'card_total': card_total,
        'bank_total': bank_total,
        'paystack_total': paystack_total,
        'total_revenue': total_revenue,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'billing/accounting_report.html', context)