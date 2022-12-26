from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from .forms import *
from django.db.models import Sum
import stripe
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View,ListView, TemplateView
def home(request):
    product=Product.objects.all().order_by("-id")[:5]
    
    context={
        'product':product
    }
    return render(request,'home.html',context)

def allProduct(request):
    all_product=Product.objects.all()
    categories=Category.objects.all()
    context={
        'all_product':all_product,
        'categories':categories
    }
    return render(request,'products.html',context)

class ProductDetailView(TemplateView):
    template_name='pro-detail.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        url_slug=self.kwargs['slug']
        product=Product.objects.get(slug=url_slug)
        product.view_count +=1
        product.save()
        context['product']=product
        return context

class AddToCartView(TemplateView):
    template_name='addtocart.html'
    def get_context_data(self, **kwargs) :
        context=super().get_context_data(**kwargs)
        # get url id 
        product_id=self.kwargs['id']
        # get products 
        product_obj=Product.objects.get(id=product_id)
        # check cart exists 
        cart_id=self.request.session.get("cart_id",None)
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            product_in_cart=cart_obj.cartproduct_set.filter(
                product=product_obj)
                # item already exists in cart 
            if product_in_cart.exists():
                cartproduct=product_in_cart.last()
                cartproduct.quantity +=1
                cartproduct.subtotal += product_obj.sell_price
                cartproduct.save()
                cart_obj.total +=product_obj.sell_price
                cart_obj.save()
                # new items added in cart 
            else:
                cartproduct=CartProduct.objects.create(
                    cart=cart_obj,
                    product=product_obj,
                    rate=product_obj.sell_price,
                    quantity=1,
                    subtotal=product_obj.sell_price
                    )
                cart_obj.total +=product_obj.sell_price
                cart_obj.save()

        else:
            cart_obj=Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct=CartProduct.objects.create(
                    cart=cart_obj,
                    product=product_obj,
                    rate=product_obj.sell_price,
                    quantity=1,
                    subtotal=product_obj.sell_price
                    )
            cart_obj.total +=product_obj.sell_price
            cart_obj.save()
        return context

class MyCartView(TemplateView):
    template_name='my-cart.html'
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        cart_id=self.request.session.get("cart_id",None)
        if cart_id:
            cart=Cart.objects.get(id=cart_id)
        else:
            cart=None
        context['cart']=cart
        return context

class ManangeCartView(View):
    def get(self,request,*args,**kwargs):
        
        cp_id=self.kwargs['cp_id']
        action=request.GET.get('action')
        cp_obj=CartProduct.objects.get(id=cp_id)
        cart_obj=cp_obj.cart

        if action=='inc':
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
        elif action=='dcr':
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action=='rmv':
            cart_obj.total -=cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect('my-cart')

class EmptyCartView(View):
    def get(self,request,*args,**kwargs):
        cart_id =request.session.get('cart_id',None)
        if cart_id:
            cart=Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total=0
            cart.save()

        return redirect('my-cart')

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000'
def checkout_session(request,ct_id):
    cart=Cart.objects.get(pk=ct_id)
    
    session=stripe.checkout.Session.create(
        
        payment_method_types=['card'],
        line_items=[
        {
            'price_data': {
            'currency': 'inr',
            'product_data': {
                'name': 'Total',
            },
            'unit_amount': cart.total*100,
            },
            'quantity': 1,
        },
        ],
        
        mode='payment',
        success_url=YOUR_DOMAIN + '/success.html',
        cancel_url=YOUR_DOMAIN + '/cancel.html',
    )
    return redirect (session.url,code=3)

def success(request,ct_id):
    cart=Cart.objects.get(pk=ct_id)
    cart.cartproduct_set.all().delete()
    cart.total=0
    cart.save(),
    return render(request,'success.html')

#  #cancel view
def cancel(request):
 return render(request,'cancel.html')
 
# class CheckoutView(TemplateView):
#     template_name=

# stripe.api_key = settings.STRIPE_SECRET_KEY
# YOUR_DOMAIN = 'http://127.0.0.1:8000'

# from .models import Order #new
# @csrf_exempt
# def create_checkout_session(request):
#  #Updated- creating Order object
#  order=Order.objects.all().total_amount()
#  session = stripe.checkout.Session.create(
#  client_reference_id=request.user.id if request.user.is_authenticated else None,
#  payment_method_types=['card'],
#  line_items=[{
#  'price_data': {
#  'currency': 'inr',
#  'product_data': {
#  'name': 'Intro to Django Course',
#  },
#  'unit_amount': 10000,
#  },
#  'quantity': 1,
#  }],
#  #Update - passing order ID in checkout to update the order object in webhook
#  metadata={
#  "order_id":id
#  },
#  mode='payment',
#  success_url=YOUR_DOMAIN + '/success.html',
#  cancel_url=YOUR_DOMAIN + '/cancel.html',
#  )
#  return JsonResponse({'id': session.id})
# @csrf_exempt
# def webhook(request):
#  print("Webhook")
#  endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
#  payload = request.body
#  sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#  event = None

#  try:
#     event = stripe.Webhook.construct_event(
#     payload, sig_header, endpoint_secret
#     )
#  except ValueError as e:
#  # Invalid payload
#     return HttpResponse(status=400)
#  except stripe.error.SignatureVerificationError as e:
#  # Invalid signature
#     return HttpResponse(status=400)

#  # Handle the checkout.session.completed event
#  if event['type'] == 'checkout.session.completed':
#  #NEW CODE
#     session = event['data']['object']
#  #getting information of order from session
    
#     price = session["total_amount"]
#     sessionID = session["id"]
#  #grabbing id of the order created
#     ID=session["metadata"]["order_id"]
#  #Updating order
#  Order.objects.filter(id=ID).update(paid=True)

#  return HttpResponse(status=200)