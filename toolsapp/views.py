from django.shortcuts import render,redirect
from .models import *
from .forms import *
def home(request):
    product=Product.objects.all()
    context={
        'product':product
    }
    return render(request,'home.html',context)

def allProduct(request):
    product=Product.objects.all()
    
    context={
        'product':product
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
# def payment(request,id):
#     print(id)
#     user=request.user
#     product=Product.objects.filter(id=id)
#     order=Order.objects.filter(product_id=id)
#     # price_arr=[]
#     # for i in order:
#     #     total=i.quantity*i.product.sell_price
#     #     price_arr.append(total)
#     context={
#         'order':order,'product':product,
#     }
#     return render(request,'payment.html',context)