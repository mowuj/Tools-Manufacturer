from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('product',allProduct,name='product'),
    path('productdetail/<slug:slug>/',ProductDetailView.as_view(),name='productdetail'),
    path('add-to-cart/<int:id>',AddToCartView.as_view(),name='addtocart'),
    path('my-cart',MyCartView.as_view(),name='my-cart'),
    # path('payPage',payPage,name='payPage'),
    # path('create-checkout-session/', create_checkout_session, name='checkout'),
    # path('success.html/', success,name='success'),
    # path('cancel.html/',cancel,name='cancel'),
    # path('webhooks/stripe/',webhook,name='webhook'),
]