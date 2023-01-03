from django.shortcuts import render,redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import authenticate,login,logout
from .models import *
from .forms import *
from django.db.models import Sum
from django.db.models import Q
import stripe
from django.conf import settings
from django.http import JsonResponse,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View,ListView, TemplateView,CreateView,FormView,DetailView,ListView
from django.urls import reverse_lazy

class ToolMixin(object):
    def dispatch(self,request,*args,**kwargs):
        cart_id=request.session.get('cart_id')
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
                cart_obj.customer=request.user.customer
                cart_obj.save()
        return super().dispatch(request,*args,**kwargs)


class CustomerRegisterView(CreateView):
    template_name='customerregister.html'
    form_class=CustomerRegisterForm
    success_url=reverse_lazy('home')
    def form_valid(self,form):
        username=form.cleaned_data.get('username')
        password=form.cleaned_data.get('password')
        email=form.cleaned_data.get('email')
        user=User.objects.create_user(username,email,password)
        form.instance.user=user
        login(self.request,user)
        return super().form_valid(form)
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url=self.request.GET.get("next")
            return next_url
        else:
            return self.success_url

class CustomerLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('home')

class CustomerLoginView(FormView):
    template_name='login.html'
    form_class=CustomerLoginForm
    success_url=reverse_lazy('home')
    def form_valid(self,form):
        username=form.cleaned_data.get('username')
        password=form.cleaned_data.get('password')
        user=authenticate(username=username,password=password)
        if user is not None and Customer.objects.filter(user=user).exists():
            login(self.request,user)
        else:
            return render(self.request,self.template_name,{'form':self.form_class,
            'error':'Invalid credentials'})
        return super().form_valid(form)
    def get_success_url(self):
        if "next" in self.request.GET:
            next_url=self.request.GET.get("next")
            return next_url
        else:
            return self.success_url


class HomeView(TemplateView):
    template_name='home.html'
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['product']=Product.objects.all().order_by("-id")[:5]
        return context

class AllProductView(TemplateView):
    template_name='products.html'
    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['all_product']=Product.objects.all()
        context['categories']=Category.objects.all()
        return context


def addProduct(request):
    return render(request,'addproduct.html')

class ProductDetailView(ToolMixin, TemplateView):
    template_name='pro-detail.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        url_slug=self.kwargs['slug']
        product=Product.objects.get(slug=url_slug)
        product.view_count +=1
        product.save()
        context['product']=product
        return context

class AddToCartView(ToolMixin, TemplateView):
    template_name='addtocart.html'
    success_url=reverse_lazy('product ')
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

class MyCartView(ToolMixin,TemplateView):
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

class EmptyCartView(ToolMixin,View):
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

    def dispatch(self,request,*args,**kwargs):
        user=request.user
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect('/register?next=checkout')
        return super().dispatch(request,*args,**kwargs)
        

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        cart_id=self.request.session.get('cart_id',None)
        
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            
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

class AddressView(ToolMixin,TemplateView):
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

class CustomerProfileView(TemplateView):
    template_name='customerprofile.html'
    def dispatch(self,request,*args,**kwargs):
        user=request.user
        if request.user.is_authenticated and Customer.objects.filter(user=user).exists():
            pass
        else:
            return redirect('/register?next=profile')
        return super().dispatch(request,*args,**kwargs)
        

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        customer=self.request.user.customer
        context['customer']=customer
        orders=Order.objects.filter(cart__customer=customer).order_by("-id")
        context['orders']=orders
        return context

class CustomerOrderDetailView(DetailView):
    template_name='customerorderdetail.html'
    model=Order
    context_object_name="ord_obj"
    def dispatch(self,request,*args,**kwargs):
        user=request.user
        if request.user.is_authenticated and Customer.objects.filter(user=user).exists():
            order_id=self.kwargs["pk"]
            order=Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer:
                return redirect('/profile')
        else:
            return redirect('/register?next=profile')
        return super().dispatch(request,*args,**kwargs)


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

class SearchView(TemplateView):
    template_name="search.html"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        # kw=self.request.GET["keyword"]
        kw=self.request.GET.get("keyword")
        results=Product.objects.filter(
            Q(title__icontains=kw) | 
            Q(description__icontains=kw) | 
            Q(category__title__icontains=kw) | 
            Q(warranty__icontains=kw))
        print(results)
        context["results"]=results
        return context

# admin 

class AdminLoginView(FormView):
    template_name='adminpages/adminlogin.html'
    form_class=CustomerLoginForm
    success_url=reverse_lazy('adminhome')

    def form_valid(self,form):
        username=form.cleaned_data.get('username')
        password=form.cleaned_data.get('password')
        user=authenticate(username=username,password=password)
        if user is not None and Admin.objects.filter(user=user).exists():
            login(self.request,user)
        else:
            return render(self.request,self.template_name,{'form':self.form_class,
            'error':'Invalid credentials'})
        return super().form_valid(form)

class AdminRequiredMixin(object):
    def dispatch(self,request,*args,**kwargs):
        user=request.user
        if request.user.is_authenticated and Admin.objects.filter(user=user).exists():
            pass
        else:
            return redirect('/adminlogin')
        return super().dispatch(request,*args,**kwargs)


class AdminHomeView(AdminRequiredMixin,TemplateView):
    template_name='adminpages/adminhome.html'

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context["pendingorders"]=Order.objects.filter(
            order_status="Order Received").order_by("-id")

        return context

class AdminOrderDetailView(AdminRequiredMixin,DetailView):
    template_name="adminpages/adminorderdetail.html"
    model=Order
    context_object_name="ord_obj"

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context["allstatus"]=ORDER_STATUS
        return context

class AdminOrderListView(AdminRequiredMixin,ListView):
    template_name="adminpages/adminorderlist.html"
    queryset=Order.objects.all().order_by("-id")
    context_object_name="allorders"

class OrderStatusChangeView(AdminRequiredMixin,View):
    def post(self,request,*args,**kwargs):
        order_id=self.kwargs["pk"]
        order_obj=Order.objects.get(id=order_id)
        new_status=request.POST.get("status")
        order_obj.order_status=new_status
        order_obj.save()
        return redirect(reverse_lazy('adminorderdetail',kwargs={"pk":order_id}))

class AdminLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('adminlogin')