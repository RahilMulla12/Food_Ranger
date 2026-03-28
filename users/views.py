from django.shortcuts import get_object_or_404, render,redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from postgis import Point
from Restaurant .models import Restaurant ,FoodItem
from Orders.models import Orders,MyCart
import geocoder
from django.utils.timezone import now
from django.db.models import Sum
from django.db.models import Prefetch
from django.contrib.gis.geos import Point




def home(request):
    return render(request, "home.html")

def login_view(request):
    if request.user.is_authenticated:
        logout(request)
        
        
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')

        user = authenticate(request, phone=phone, password=password)

        if user is not None:
            login(request, user)

            if getattr(user, "is_superuser", False):
                return redirect("admin_dashboard")
            elif getattr(user, "is_rider", False):
                return redirect("Delivery_dashboard")
            elif getattr(user, "is_restaurant_owner", False):
                return redirect("Restaurent")
            else:
                return redirect("menu")

        else:
            messages.error(request, "Invalid phone or password")

    return render(request, "login.html")    

User =get_user_model()
def register(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        username = request.POST.get("username")

        role = request.POST.get("role")

        if User.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered")
            return redirect("register")

        user = User.objects.create_user(
            phone=phone,
            username=username,
            password=password,
            is_customer=(role == "customer"),
            is_rider=(role == "rider"),
            is_restaurant_owner=(role == "restaurant"),
        )

        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "register.html")


def logout_view(request):
    logout(request)
    return redirect("login")


def MyOrders(request):
    orders = Orders.objects.all()

    return render(request, "MyOrders.html", {"orders": orders})


from django.contrib.auth.decorators import login_required

@login_required
def restaurant_dashboard(request):
    restaurant_info = Restaurant.objects.filter(owner=request.user).first()

    if not restaurant_info:
        messages.warning(request, "Please create your restaurant first.")
        return redirect('create_restaurant') 

    orders = Orders.objects.filter(restaurant=restaurant_info)

    return render(request, "restaurant_dash.html", {
        "restaurant": restaurant_info,
        "orders": orders
    })





from django.db.models import Prefetch
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two coordinates."""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def Menu(request):
    available_items = FoodItem.objects.filter(is_available=True)
    restaurants = Restaurant.objects.prefetch_related(
        Prefetch('food_items', queryset=available_items)
    ).filter(is_open=True)

    # ✅ get user location from session
    user_lat = request.session.get('user_lat')
    user_lon = request.session.get('user_lon')

    radius_km = 10  # show restaurants within 10 km

    if user_lat and user_lon:
        nearby = []
        for r in restaurants:
            # Restaurant.location is a PointField → r.location.y=lat, r.location.x=lon
            dist = haversine(user_lat, user_lon, r.location.y, r.location.x)
            if dist <= radius_km:
                r.location = round(dist, 1)  # attach distance to object
                nearby.append(r)

        # sort closest first
        nearby.sort(key=lambda r: r.distance)
        restaurants = nearby
        location_detected = True
    else:
        location_detected = False
        for r in restaurants:
            r.location = None

    context = {
        'restaurants': restaurants,
        'location_detected': location_detected,
        'user_lat': user_lat,
        'user_lon': user_lon,
    }
    return render(request, "menu.html", context)


def delivery_dashboard(request):
    orders = [
        {
            "id": 101,
            "customer": "Rahul Sharma",
            "address": "MG Road, Bangalore",
            "restaurant": "Burger Hub",
            "payment_type":"paid",
            "amount": 350,
            "lat": 12.9716,
            "lng": 77.5946,
        },
        {
            "id": 102,
            "customer": "Anita Patel",
            "address": "Andheri West, Mumbai",
            "restaurant": "Pizza Point",
            "payment_type":"Cash on delivery",
            "amount": 520,
            "lat": 19.1364,
            "lng": 72.8296,
        }
    ]

    return render(request, "delivery_dash.html", {"orders": orders})

def base(request):
    details=[
        {"city": "current location"}
    ]
    return render(request , "base.html",{"details":details})

def add_to_cart(request, food_id):
    food = FoodItem.objects.get(id=food_id)

    cart_item, created = MyCart.objects.get_or_create(
        user=request.user,
        Food_item=food,
        defaults={   
            "price": food.price,
            "quantity": 1
        }
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')


def cart(request):
    cart_items=MyCart.objects.filter(user=request.user)
    
    total_price=0
    for items in cart_items:
        total_price+=items.total_price()
        
    return render(request,'cart.html',{
        "cart_items":cart_items,
        "total":total_price
    })
    
def remove_from_cart(request ,cart_id):
    cart_item=MyCart.objects.get(id=cart_id,user=request.user)
    cart_item.delete()
    return redirect('cart')
    
@login_required
def restaurant_profile(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()

    if not restaurant:
        return redirect('create_restaurant')

    return render(request, "Restaurant_profile.html", {"restaurant": restaurant})

def new_dishes(request):
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    food_items = FoodItem.objects.filter(restaurant=restaurant)

    if request.method == 'POST' and 'add_dish' in request.POST:
        name       = request.POST.get('name')
        price      = request.POST.get('price')
        is_available = request.POST.get('is_available') == 'True'
        Food_image = request.FILES.get('Food_image')

        FoodItem.objects.create(
            restaurant   = restaurant,
            name         = name,
            price        = price,
            is_available = is_available,
            Food_image   = Food_image,
        )
        return redirect('new_dishes')   # PRG pattern — prevents duplicate on refresh

    context = {
        'restaurant': restaurant,
        'food_items': food_items,
    }
    return render(request, "new_dishes.html", context)


def buy_item(request, food_id):
    food = get_object_or_404(FoodItem, id=food_id)

    if request.method == "POST":
        quantity = int(request.POST.get("quantity", 1))
        total_price = food.price * quantity

        Orders.objects.create(
         customer=request.user,
         food=food,
         restaurant=food.restaurant,
         quantity=quantity,
         total_price=total_price,
)
        request.session["buy_item"]={
            "food_id":food_id,
            "food_name":food.name,
            "quantity":1,
            "price":food.price
        }
        return redirect("Payments")

    return render(request, "user_order.html", {"food": food})

def Payments(request):
     
    return render(request,'payments.html')

def order_sucsess(request):
    
    return render(request,'order_sucsess.html')

def update_order_status(request,order_id):
    order = Orders.objects.get( id=order_id)
    
    if request.method=="POST":
        status=request.POST.get("status")
        order.status=status
        order.save()
        
    return redirect("Restaurent")  
        
def user_profile(request):
   return render(request,"user_profile.html")
def payment(request):

    cart_items = MyCart.objects.filter(user=request.user)

    total = 0
    for item in cart_items:
        total += item.total_price()

    if request.method == "POST":

        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")

        print(latitude, longitude)

    return render(request,"payments.html",{"total":total})

def current_location(request):
    g = geocoder.ip('me')

    if g.ok and g.latlng:
        lat = g.latlng[0]
        lon = g.latlng[1]
        request.session['user_lat'] = lat
        request.session['user_lon'] = lon
        
        if request.user =='is_restuarant':
         restaurant , create = Restaurant.objects.get_or_create(owner=request.user)
         restaurant.location=Point(lon,lat)
         restaurant.save()
        elif request.user == 'is_user':
            user, created = User.objects.get_or_create(user=request.user)
            user.location = Point(lon, lat) # type: ignore
            user.save()
    else:
        lat, lon = None, None
        
        
    
    context = {'latitude': lat, 'longitude': lon}
    return render(request, "currentlocation.html", context)



@login_required
def res_manage(request):
    restaurant = Restaurant.objects.filter(owner=request.user).first()

    if not restaurant:
        return redirect('create_restaurant')

    orders = Orders.objects.filter(restaurant=restaurant)

    accepted_orders = orders.filter(
        status__in=['ACCEPTED', 'PREPARING', 'OUT_OF_DELIVERY']
    ).count()

    rejected_orders = orders.filter(status="CANCELED").count()

    delivered_today = orders.filter(
        status='DELIVERED',
        created_at__date=now().date()
    ).count()

    total_sales = orders.filter(
        status='DELIVERED'
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    today_sales = orders.filter(
        status='DELIVERED',
        created_at__date=now().date()
    ).aggregate(Sum('total_price'))['total_price__sum'] or 0

    recent_orders = orders.order_by('-created_at')[:5]

    return render(request, "res_manage.html", {
        'restaurant': restaurant,
        'food_items': FoodItem.objects.filter(restaurant=restaurant),  
        'total_sales': total_sales,
        'accepted_orders': accepted_orders,
        'rejected_orders': rejected_orders,
        'delivered_today': delivered_today,
        'today_sales': today_sales,
        'recent_orders': recent_orders,
    })
@login_required
def create_restaurant(request):
    if request.method == "POST":
        name = request.POST.get("name")
        address = request.POST.get("address")
        lat = request.POST.get("lat")
        lon = request.POST.get("lon")

        from django.contrib.gis.geos import Point

        Restaurant.objects.create(
            owner=request.user,
            name=name,
            address=address,
            location=Point(float(lon), float(lat))
        )

        return redirect("Restaurent")  # your dashboard

    return render(request, "create_restaurant.html")