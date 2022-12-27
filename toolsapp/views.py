from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import *
from .forms import *
from django.db.models import Sum
import stripe
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View,ListView, TemplateView,CreateView
from django.urls import reverse_lazy
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

def addProduct(request):
    return render(request,'addproduct.html')

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

class ManageCartView(View):
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


class CheckoutView(CreateView):
    template_name='checkout.html'
    form_class=CheckoutForm
    success_url=reverse_lazy('address')

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        cart_id=self.request.session.get('cart_id',None)
        print('cart-id',cart_id)
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            print(cart_obj)
        else:
            cart_obj=None
        context['cart']=cart_obj
        return context

    def form_valid(self,form):
        cart_id=self.request.session.get('cart_id')
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            form.instance.cart=cart_obj
            form.instance.subtotal=cart_obj.total
            form.instance.discount=0
            form.instance.total=cart_obj.total
            form.instance.order_status='Order Received'
            # del self.request.session['cart_id']
        else:
            return redirect('home')

        return super().form_valid(form)

class AddressView(TemplateView):
    template_name='checkoutaddress.html'
    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        cart_id=self.request.session.get('cart_id',None)
        print('cart-id',cart_id)
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            print(cart_obj)
        else:
            cart_obj=None
        context['cart']=cart_obj
        return context

def allOrder(request):
    cart=Cart.objects.all()
    context={
        'cart':cart
    }
    return render(request,'allorder.html',context)

stripe.api_key = settings.STRIPE_SECRET_KEY
YOUR_DOMAIN = 'http://127.0.0.1:8000'
def checkout_session(request,id):
    cart=Cart.objects.get(id=id)
    
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
        success_url=YOUR_DOMAIN + '/success',
        cancel_url=YOUR_DOMAIN + '/cancel.html',
    )
    del request.session['cart_id']
    return redirect (session.url,code=3)

def success(request):
    
    return render(request,'success.html')

#  #cancel view
def cancel(request):
 return render(request,'cancel.html')