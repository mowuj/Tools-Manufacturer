from django.urls import path
from .views import *

urlpatterns = [
    path('slider',slider,name='slider'),
    path('',HomeView.as_view(),name='home'),
    path('product',AllProductView.as_view(),name='product'),
    path('addproduct',addProduct,name='addproduct'),
    path('productdetail/<slug:slug>/',ProductDetailView.as_view(),name='productdetail'),
    path('add-to-cart/<int:id>',AddToCartView.as_view(),name='addtocart'),
    path('my-cart',MyCartView.as_view(),name='my-cart'),
    path('manage-cart/<int:cp_id>',ManageCartView.as_view(),name='manage-cart'),
    path('empty-cart',EmptyCartView.as_view(),name='empty-cart'),
    # path('address/',AddressView.as_view(),name='address'),
    path('checkout/',CheckoutView.as_view(),name='checkout'),
    path('checkout_session/<int:pk>/', checkout_session, name='checkout_session'),
    path('success', success,name='success'),
    path('cancel.html/',cancel,name='cancel'),
    path('allorder',allOrder,name='allorder'),
    path('search/',SearchView.as_view(),name="search"),
    path('register',CustomerRegisterView.as_view(),name='register'),
    path('logout',CustomerLogoutView.as_view(),name='logout'),
    path('login',CustomerLoginView.as_view(),name='login'),
    path('profile',CustomerProfileView.as_view(),name='profile'),
    path('profile/order<int:pk>',CustomerOrderDetailView.as_view(),name='customerorderdetail'),
    path('adminlogin',AdminLoginView.as_view(),name='adminlogin'),
    path('adminlogout',AdminLogoutView.as_view(),name='adminlogout'),
    path('adminhome',AdminHomeView.as_view(),name='adminhome'),
    path('adminorder/<int:pk>',AdminOrderDetailView.as_view(),name='adminorderdetail'),
    path('adminallorders',AdminOrderListView.as_view(),name='adminorderlist'),
    path("admin-order-<int:pk>-change/",OrderStatusChangeView.as_view(),name="orderstatuschange"),

]