from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('product',allProduct,name='product'),
    path('productdetail/<slug:slug>/',ProductDetailView.as_view(),name='productdetail'),
    path('add-to-cart/<int:id>',AddToCartView.as_view(),name='addtocart'),
    path('my-cart',MyCartView.as_view(),name='my-cart'),
    path('manage-cart/<int:cp_id>',ManangeCartView.as_view(),name='manage-cart'),
    path('empty-cart',EmptyCartView.as_view(),name='empty-cart'),
    # path('payPage',payPage,name='payPage'),
    path('checkout_session/<int:ct_id>', checkout_session, name='checkout_session'),
    path('success.html', success,name='success'),
    path('cancel.html/',cancel,name='cancel'),
    # path('checkout/',CheckoutView.as_view(),name='checkout'),
    # path('webhooks/stripe/',webhook,name='webhook'),
]