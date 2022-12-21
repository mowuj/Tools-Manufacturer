from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from .forms import *
import stripe
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
def home(request):
    product=Product.objects.all()
    
    context={
        'product':product
    }
    return render(request,'home.html',context)

def allProduct(request):
    product_list=Product.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(product_list, 5)
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    context={
        'products':products
    }
    return render(request,'all-product.html',context)

def productDetail(request,id):
    details=Product.objects.filter(id=id)
    
    form=OrderForm(request.POST)
    if request.method=='POST':
        if form.is_valid():
            ord=form.save(commit=False)
            ord.user=request.user
            ord.product_id=id
            ord.save()
            context={'form':form}
            return redirect('payment',id=id)
    form=OrderForm()
    context={
        'details':details,'form':form
    }
    return render(request,'pro-detail.html',context)

def user_order(request):
    order=Order.objects.filter(user=request.user)
    context={
        'order':order
    }
    return render(request,'order.html',context)
def payPage(request):
    return render(request,'checkout.html')
def payment(request,id):
    orders=Order.objects.filter(id=id)
    print(orders)
    context={
        'orders':orders
    }
    return render(request,'payment.html',context)
def success(request):
 return render(request,'success.html')

 #cancel view
def cancel(request):
 return render(request,'cancel.html')
 
stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000'

@csrf_exempt
def create_checkout_session(request):
    session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=[{
    'price_data': {
    'currency': 'inr',
    'product_data': {
    'name': 'Intro to Django Course',
    },
    'unit_amount': 10000,
    },
    'quantity': 1,
    }],
    mode='payment',
    success_url=YOUR_DOMAIN + '/success.html',
    cancel_url=YOUR_DOMAIN + '/cancel.html',
    )
    return JsonResponse({'id': session.id})

@csrf_exempt
def webhook(request):
 endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
 payload = request.body
 sig_header = request.META['HTTP_STRIPE_SIGNATURE']
 event = None

 try:
    event = stripe.Webhook.construct_event(
    payload, sig_header, endpoint_secret
    )
 except ValueError as e:
 # Invalid payload
    return HttpResponse(status=400)
 except stripe.error.SignatureVerificationError as e:
 # Invalid signature
    return HttpResponse(status=400)

 # Handle the checkout.session.completed event
 if event['type'] == 'checkout.session.completed':
    print("Payment was successful.")
 # TODO: run some custom code here

 return HttpResponse(status=200)