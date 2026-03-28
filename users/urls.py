from django.conf import settings
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name="login"),
    path('Menu/', views.Menu, name="menu"),            
    path('register/', views.register, name="register"),
    path('myorders/', views.MyOrders, name="myorders"),
    path('delivery/',views.delivery_dashboard,name="Delivery_dashboard"),
    path('restaurent/',views.restaurant_dashboard,name="Restaurent"),
    path('cart/',views.cart,name='cart'),
    path('logout/', views.logout_view,name='logout'),
    path('restaurant_profile/',views.restaurant_profile,name="restaurant_profile"),
    path('new_dishes/',views.new_dishes,name="new_dishes"),
    path('buy/<int:food_id>/', views.buy_item, name='buy_item'),
    path('order_sucsess/',views.order_sucsess,name='order_sucsess'),
    path('update-order/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('profile/',views.user_profile,name='user_profile'),
    path('add_to_cart/<int:food_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:cart_id>/',views.remove_from_cart,name="remove_from_cart"),
    path('Payments/',views.Payments,name="Payments"),
    path('currentlocation/',views.current_location,name="current_location"),
    path('res_manage/',views.res_manage,name="res_manage"),
    path('create-restaurant/', views.create_restaurant, name='create_restaurant'),
    

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)