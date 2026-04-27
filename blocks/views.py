import uuid
from datetime import datetime
import requests
import json
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from .models import BlockType, DeliveryZone, Order
from django.contrib.auth import login
from .forms import RegistrationForm

def membership_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Hifadhi namba ya simu na location kwenye Profile
            user.profile.phone_number = form.cleaned_data.get('phone_number')
            user.profile.location = form.cleaned_data.get('location')
            user.set_password(form.cleaned_data.get('password'))
            user.save()
            
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'blocks/membership.html', {'form': form})

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'blocks/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

# 1. Ukurasa wa Nyumbani
def home_view(request):
    blocks = BlockType.objects.all()
    zones = DeliveryZone.objects.all()
    return render(request, 'blocks/home.html', {'blocks': blocks, 'zones': zones})

# 2. Calculator ya Matofali
def calculator_view(request):
    result = None
    if request.method == "POST":
        try:
            wall_area = float(request.POST.get('wall_area', 0))
            blocks_needed = wall_area * 12 
            result = round(blocks_needed)
        except ValueError:
            result = "Tafadhali jaza namba sahihi"
    return render(request, 'blocks/calculator.html', {'result': result})

# 3. Kutengeneza Oda (Inaitwa na submitOrder kwenye JS)
def place_order(request):
    if request.method == "POST":
        try:
            block_id = request.POST.get('block_id')
            qty = int(request.POST.get('quantity'))
            zone_id = request.POST.get('zone_id')
            phone = request.POST.get('phone')

            block = get_object_or_404(BlockType, id=block_id)
            zone = get_object_or_404(DeliveryZone, id=zone_id)
            
            # Piga hesabu kwa kutumia price_per_block kama ilivyo kwenye model yako
            total = (block.price_per_block * qty) + zone.delivery_fee

            # Hifadhi oda
            order = Order.objects.create(
                block_type=block,
                quantity=qty,
                delivery_zone=zone,
                total_price=total,
                customer_phone=phone,
                status='PENDING'
            )

            return JsonResponse({'status': 'success', 'order_id': order.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

# 4. Ukurasa wa Malipo (Checkout)
def checkout_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'blocks/checkout.html', {'order': order})

# 5. Kuchakata Malipo ya PawaPay

def process_payment(request):
    if request.method == "POST":
        try:
            order_id = request.POST.get('order_id')
            provider = request.POST.get('provider')
            order = Order.objects.get(id=order_id)

            phone = order.customer_phone
            if phone.startswith('0'):
                phone = '255' + phone[1:]
            
            deposit_id = str(uuid.uuid4())

            # Tengeneza muda wa sasa katika mfumo wa ISO 8601 (mfano: 2026-04-27T08:30:00Z)
            # PawaPay wanataka muda uwe na herufi 'Z' mwishoni (UTC)
            now_utc = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

            payload = {
                "depositId": deposit_id,
                "amount": str(int(order.total_price)),
                "currency": "TZS",
                "correspondent": provider.upper(),
                "payer": {
                    "type": "MSISDN",
                    "address": { "value": phone }
                },
                "customerTimestamp": now_utc, # <--- Hapa ndipo tulikuwa tumepungukiwa!
                "statementDescription": f"Dozee Order {order.id}"
            }

            headers = {
                "Authorization": f"Bearer {settings.PAWAPAY_API_TOKEN}",
                "Content-Type": "application/json"
            }

            url = f"{settings.PAWAPAY_BASE_URL}/deposits"
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            
            if response.status_code in [200, 202]:
                return JsonResponse({'status': 'success', 'message': 'STK Push imetumwa! Weka PIN.'})
            else:
                return JsonResponse({'status': 'error', 'message': f"PawaPay Error: {response.text}"})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid Request'})
# 6. Mrejesho kutoka PawaPay
@csrf_exempt
def pawapay_callback(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            deposit_id = data.get('depositId')
            status = data.get('status') 

            if status == 'COMPLETED':
                # Hapa unaweza kuongeza logic ya kupata oda kupitia deposit_id
                # Kwa sasa tunaprint tuone mrejesho
                print(f"Malipo ya {deposit_id} yamefanikiwa!")
            
            return JsonResponse({'status': 'received'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'method not allowed'}, status=405)

def about_view(request):
    return render(request, 'blocks/about.html')

def contact_view(request):
    return render(request, 'blocks/contact.html')