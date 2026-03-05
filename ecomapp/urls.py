from django.urls import path
from . import views 
from streamlit import user
from ecomapp import views
from . import views 


urlpatterns = [
    path('',views.home,name='home'),
    path('login',views.handlelogin,name='handlelogin'),
    path('signup',views.signup,name='signup'),
    path('logout',views.logouts,name='logouts'),
    path('about', views.about, name="AboutUs"),
    path('contactus',views.contactus,name='contactus'),
    path('tracker', views.tracker, name="TrackingStatus"),
    path('products/<int:myid>', views.productView, name="ProductView"),
    path('request-reset-email/', views.request_reset_email, name="request-reset-email"),
    path('set-new-password/<uidb64>/<token>/', views.set_new_password, name="set-new-password"),
    path('payment/success/', views.payment_success, name="PaymentSuccess"),
    path('checkout/',views.checkout, name="Checkout"),
]