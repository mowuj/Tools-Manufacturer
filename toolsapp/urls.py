from django.urls import path
from .views import *

urlpatterns = [
    path('',home,name='home'),
    path('product',allProduct,name='product'),
    path('detail/<int:id>',productDetail,name='detail'),
    path('order',user_order,name='order'),
    path('payment/<int:id>',payment,name='payment'),
    path('payPage',payPage,name='payPage'),
    path('create-checkout-session/', create_checkout_session, name='checkout'),
    path('success.html/', success,name='success'),
    path('cancel.html/',cancel,name='cancel'),
    path('webhooks/stripe/',webhook,name='webhook'),
]