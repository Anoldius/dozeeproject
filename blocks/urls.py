from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('place-order/', views.place_order, name='place_order'),
    path('checkout/<int:order_id>/', views.checkout_view, name='checkout_view'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('pawapay-callback/', views.pawapay_callback, name='pawapay_callback'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('membership/', views.membership_view, name='membership'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]