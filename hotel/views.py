import re
from django.shortcuts import render,redirect
import requests
from hotel.forms import BlogForm, ContactForm
from hotel.models import Coupon, Hotel,Booking,ActivityLog,staffOnDuty,RoomType,Room,Notification,Bookmark,Review
from django.contrib import messages
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from decimal import Decimal
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.db.models import Q
from .utils.currency_utils import convert_currency,get_available_currencies

def index(request):
    hotels=Hotel.objects.filter(status="Live")
    context={
        'hotels':hotels
    }
    return render(request,"hotel/hotel.html",context)

def about(request):
    return render(request,"hotel/about.html")

def services(request):
    return render(request,"hotel/services.html")

def packages(request):
    hotels=Hotel.objects.filter(status="Live")
    context={
        'hotels':hotels
    }
    return render(request,"hotel/packages.html",context)

def blog(request):
    blogs = Blog.objects.all().order_by('-created_at')  # Fetch all blogs, newest first
    
    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('hotel:blog')
    else:
        form = BlogForm()
    
    context = {
        'blogs': blogs,
        'form': form,
    }
    
    return render(request, "hotel/blog.html", context)

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('hotel:contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'hotel/contact.html', {'form': form})



def hotel_detail(request, slug):
    hotel = Hotel.objects.get(status="Live", slug=slug)

    if request.user.is_authenticated:
        bookmark=Bookmark.objects.filter(user=request.user,hotel=hotel)
    else:
        bookmark=None
    
    all_reviews = Review.objects.filter(hotel=hotel)
    
    try:
        reviews = Review.objects.filter(user=request.user,hotel=hotel)
    except:
        reviews=None
        
     # Fetch weather data by default to show in modal
    city = hotel.address.split(',')[1]  # Assuming the first part of the address is the city
    weather_data = get_weather_data(city)
    advice = get_weather_advice(weather_data['description']) if weather_data else None
    
    user_currency = request.GET.get('currency', 'USD')  # Default to USD if not provided

    room_types = RoomType.objects.filter(hotel=hotel)
    
    # Convert room prices
    for room in room_types:
        room.converted_price = convert_currency(room.price, from_currency="USD", to_currency=user_currency)

    currencies = get_available_currencies()

    context={
        "hotel":hotel,
        "bookmark":bookmark,
        "reviews":reviews,
        "all_reviews":all_reviews,
        "weather_data": weather_data,
        "advice": advice,
        "room_types": room_types,
        "user_currency": user_currency,
        "currencies": currencies,
    }
    return render(request,"hotel/hotel_detail.html",context)



def is_room_available(room, check_in_date, check_out_date):
    """
    Check if a room is available for the given date range
    """
    # Convert string dates to datetime objects if they're strings
    if isinstance(check_in_date, str):
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').date()
    if isinstance(check_out_date, str):
        check_out_date = datetime.strptime(check_out_date, '%Y-%m-%d').date()
    
    # Check if there are any overlapping bookings
    overlapping_bookings = Booking.objects.filter(
        room=room,
        check_in_date__lt=check_out_date,
        check_out_date__gt=check_in_date,
        is_active=True,
        is_cancelled=False
    ).exists()
    
    return not overlapping_bookings

def room_type_detail(request, slug, rt_slug):
    hotel = Hotel.objects.get(status="Live",slug=slug)
    room_type = RoomType.objects.get(hotel=hotel,slug=rt_slug)
    
    checkin = request.GET.get("checkin")
    checkout = request.GET.get("checkout")
    adult = request.GET.get("adult")
    children = request.GET.get("children")

    # Get all rooms of this type
    all_rooms = Room.objects.filter(room_type=room_type, is_avaliable=True)
    
    # If check-in and check-out dates are provided, filter available rooms
    if checkin and checkout:
        available_rooms = [
            room for room in all_rooms 
            if is_room_available(room, checkin, checkout)
        ]
    else:
        available_rooms = all_rooms
    
    context = {
        "hotel": hotel,
        "room_type": room_type,
        "rooms": available_rooms,
        "checkin": checkin,
        "checkout": checkout,
        "adult": adult,
        "children": children,
    }
    return render(request, "hotel/room_type_detail.html", context)



def selected_rooms(request):
    total=0
    room_count=0
    total_days=0
    adult=0
    children=0
    checkin=""
    checkout=""
    if 'selection_data_obj' in request.session:
        if request.method == "POST":
            for h_id, item in request.session['selection_data_obj'].items():
               id = int(item['hotel_id'])  
               checkin = item['checkin']  
               checkout = item['checkout']  
               adult = int(item['adult'])  
               children = int(item['children'])  
               room_type_ = int(item['room_type'])  
               room_id = int(item['room_id'])

               user=request.user
               hotel=Hotel.objects.get(id=id) 
               room = Room.objects.get(id=room_id)
               room_type=RoomType.objects.get(id=room_type_)
            
            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checkout_date = datetime.strptime(checkout, date_format)
            time_difference=checkout_date - checkin_date
            total_days=time_difference.days

            full_name=request.POST.get('full_name')
            email=request.POST.get('email')
            phone=request.POST.get('phone')

            booking = Booking.objects.create(
                hotel=hotel,
                room_type=room_type,
                check_in_date=checkin,
                check_out_date=checkout,
                total_days=total_days,
                num_adults=adult,
                num_children=children,
                full_name=full_name,
                email=email,
                phone=phone,
                user=request.user or None,
               

            )

            # if request.user.is_authenticated:
            #     booking.user=request.user
            #     booking.save()
            # else:
            #     booking.user==None
            #     booking.save()
            for h_id, item in request.session['selection_data_obj'].items():
                room_id=int(item["room_id"])
                room=Room.objects.get(id=room_id)
                booking.room.add(room)
                room_count += 1
                days=total_days
                price=room_type.price
                room_price= price * room_count
                total = room_price * days
            
            booking.total += float(total)
            booking.before_discount += float(total)
            booking.save()
            # messages.success(request,"checkout Now")
            return redirect("hotel:checkout",booking.booking_id)

        hotel = None
        for h_id, item in request.session['selection_data_obj'].items():
            id = int(item['hotel_id'])  # Corrected here
            checkin = item['checkin']  # Corrected here
            checkout = item['checkout']  # Corrected here
            adult = int(item['adult'])  # Corrected here
            children = int(item['children'])  # Corrected here
            room_type_ = int(item['room_type'])  # Corrected here
            room_id = int(item['room_id'])  # Corrected here

            room_type = RoomType.objects.get(id=room_type_)

            date_format = "%Y-%m-%d"
            checkin_date = datetime.strptime(checkin, date_format)
            checkout_date = datetime.strptime(checkout, date_format)
            time_difference=checkout_date - checkin_date
            total_days=time_difference.days
            
            room_count += 1
            days=total_days
            price=room_type.price
            room_price= price * room_count
            total = room_price * days

            hotel = Hotel.objects.get(id=id)
        context={
            "data":request.session['selection_data_obj'],
            "total_selected_items":len(request.session['selection_data_obj']),
            "total":total,
            "total_days":total_days,
            "adult":adult,
            "children":children,
            "checkin":checkin,
            "checkout":checkout,
            "hotel":hotel,

        }
        return render(request, "hotel/selected_rooms.html",context)

    else:
        messages.warning(request, "No selected rooms yet.")
        return redirect("/")






def checkout(request,booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    if request.method=="POST":
        code=request.POST.get("code")
        try:
             coupon = Coupon.objects.get(code__iexact=code,active=True)
             if coupon in booking.coupons.all():
                 messages.warning(request,"Coupon already activated")
                 return redirect("hotel:checkout",booking.booking_id)
             else:
                 if coupon.type=="Percentage":
                     discount=booking.total * coupon.discount / 100
                 else:
                     discount=coupon.discount
                 booking.coupons.add(coupon)
                 booking.total -= discount
                 booking.saved += discount
                 booking.save()
                 messages.success(request,"Coupon Activated")
                 return redirect("hotel:checkout",booking.booking_id)
                 
        except:
            messages.error(request,"Coupon Does Not Exist")
            return redirect("hotel:checkout",booking.booking_id)
    context={
        "booking":booking,
        "stripe_publishable_key":settings.STRIPE_PUBLIC_KEY,
    }

    return render(request,"hotel/checkout.html",context)

@csrf_exempt
def create_checkout_session(request,booking_id):
    booking = Booking.objects.get(booking_id=booking_id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
   
    checkout_session = stripe.checkout.Session.create(
        customer_email=booking.email,
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"Booking for {booking.hotel.name}",
                        'description': f"Check-in: {booking.check_in_date}, Check-out: {booking.check_out_date}"
                    },
                    'unit_amount': int(booking.total * 100)  # Convert to cents
                },
                'quantity': 1
            }
        ],
        mode='payment',
        success_url=request.build_absolute_uri(
            reverse("hotel:success", args=[booking.booking_id])
        ) + f"?session_id={{CHECKOUT_SESSION_ID}}&success_id={booking.success_id}&booking_total={booking.total}",
        cancel_url=request.build_absolute_uri(reverse("hotel:failed", args=[booking.booking_id]))
    )
    
    booking.payment_status = "Processing"
    booking.stripe_payment_intent = checkout_session.id
    booking.save()

    return JsonResponse({
        "sessionId": checkout_session.id
    })

def payment_success(request,booking_id):
    success_id=request.GET.get('success_id')
    booking_total=request.GET.get('booking_total')

    if success_id and booking_total:

        success_id=success_id.rstrip("/")
        booking_total=booking_total.rstrip("/")
       
        booking=Booking.objects.get(booking_id=booking_id,success_id=success_id)

        if booking.total==Decimal(booking_total):
            print("Booking total matched")
            if booking.payment_status=="Processing":
                booking.payment_status="paid"
                booking.is_active=True
                booking.save()

                 # Send Confirmation Email with HTML content
                subject = "Booking Confirmed: Your Hotel Reservation Details"
                context = {
                    'user': booking.user,
                    'full_name': booking.full_name,
                    'hotel': booking.hotel.name,
                    'room_type': booking.room_type.type,
                    'check_in_date': booking.check_in_date,
                    'check_out_date': booking.check_out_date,
                    'total': booking.total,
                    'saved': booking.saved,
                    'payment_status': booking.payment_status,
                    'booking_id': booking.booking_id,
                    'num_adults': booking.num_adults,
                    'num_children': booking.num_children,
                }

                # Render the HTML content from template
                html_message = render_to_string('hotel/booking_confirmation_email.html', context)

                send_mail(
                    subject,
                    'This is a confirmation email. If you cannot view it properly, please view it as HTML.',  # plain-text fallback message
                    'mkambika287@gmail.com',  # Replace with your email
                    [booking.email],  # Send the email to the booking email
                    fail_silently=False,
                    html_message=html_message  # Specify the HTML version of the message
                )

                noti =Notification.objects.create(
                    booking=booking,
                    type="Booking Confirmed",
                )
                if request.user.is_authenticated:
                    noti.user=request.user
                else:
                    noti.user=None
                noti.save()

                if 'selection_data_obj' in request.session:
                    del request.session['selection_data_obj']
            else:
                messages.success(request,"Payment made already,thanks for your patronage")
                # return redirect("/")
        else:
           
            messages.error(request,"error:payment manipulation detected")
    context={
        "booking":booking
    }
    
    return render(request,"hotel/payment_success.html",context)

def payment_failed(request,booking_id):
    return render(request,"hotel/payment_failed.html")

def update_room_status(request):
    today = timezone.now().date()
    bookings = Booking.objects.filter(is_active=True, payment_status="paid")
    
    for booking in bookings:
        # Handle check-in logic
        if not booking.checked_in_tracker:
            if booking.check_in_date > today:
                # Future booking
                booking.checked_in = False
                booking.checked_in_tracker = False
                booking.save()

                for room in booking.room.all():
                    if not room.is_avaliable:
                        room.is_avaliable = True
                        room.save()
            else:
                # Current or past booking (checked in)
                booking.checked_in = True
                booking.checked_in_tracker = True
                booking.save()

                for room in booking.room.all():
                    if room.is_avaliable:
                        room.is_avaliable = False
                        room.save()
        
        # Handle check-out logic
        if not booking.checked_out_tracker:
            if booking.check_out_date <= today:
                # Booking has ended (checked out)
                booking.checked_out = True
                booking.checked_out_tracker = True
                booking.checked_in = False
                booking.save()

                for room in booking.room.all():
                    if not room.is_avaliable:
                        room.is_avaliable = True
                        room.save()
            else:
                # Booking is ongoing
                booking.checked_out = False
                booking.checked_out_tracker = False
                booking.save()

                for room in booking.room.all():
                    if room.is_avaliable:
                        room.is_avaliable = False
                        room.save()

    return HttpResponse(today)

def generate_invoice(request, booking_id):
    # Fetch the booking object
    booking = Booking.objects.get(booking_id=booking_id)

    # Prepare context for the invoice template
    context = {
        'user': booking.user,
        'full_name': booking.full_name,
        'customer_email': booking.email,
        'customer_phone': booking.phone,
        'hotel': booking.hotel.name,
        'address': booking.hotel.address,
        'hotel_email': booking.hotel.email,
        'hotel_phone': booking.hotel.mobile,
        'room_price': booking.room_type.price,
        'room_type': booking.room_type.type,
        'check_in_date': booking.check_in_date,
        'check_out_date': booking.check_out_date,
        'total_days': booking.total_days,
        'total': booking.total,
        'saved': booking.saved,
        'payment_status': booking.payment_status,
        'booking_id': booking.booking_id,
        'num_adults': booking.num_adults,
        'num_children': booking.num_children,
    }

    # Render HTML for the invoice using the template
    html_content = render_to_string('hotel/invoice_template.html', context)

    # Create a response object to return the PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{booking.booking_id}.pdf"'

    # Generate the PDF from HTML content
    pisa_status = pisa.CreatePDF(html_content, dest=response)

    # Check if the PDF was created successfully
    if pisa_status.err:
        return HttpResponse('We had some errors while generating the PDF document.')

    return response

from django.shortcuts import render
from django.db.models import Q  # <-- Make sure to import Q here
from .models import Blog, Hotel
def search_hotels(request):
    query = request.GET.get('query', '').lower().strip()  # Convert to lowercase and strip whitespace
    hotels = Hotel.objects.all()

    # Clean the query by removing common phrases
    if query:
        # Remove phrases like 'hotels in', 'places in', 'stay in'
        cleaned_query = re.sub(r"(hotels in|places in|stay in|accommodation in|near|at|around)\s+", "", query)
        
        # Filter hotels by name or address using cleaned query
        hotels = hotels.filter(
            Q(name__icontains=cleaned_query) | 
            Q(address__icontains=cleaned_query)
        )

    return render(request, 'hotel/search_results.html', {'hotels': hotels, 'query': query})

from django.shortcuts import render
from django.db.models import Count
from django.db.models.functions import TruncMonth
from .models import Booking, RoomType, Hotel

def booking_dashboard(request):
    # Booking by City
    city_data = (
        Hotel.objects.values('address')
        .annotate(total_bookings=Count('booking'))
        .order_by('-total_bookings')
    )
    city_labels = [item['address'] for item in city_data]
    city_counts = [item['total_bookings'] for item in city_data]

    # Room Type Popularity
    room_type_data = (
        RoomType.objects.values('type')
        .annotate(total_bookings=Count('booking'))
        .order_by('-total_bookings')
    )
    room_type_labels = [item['type'] for item in room_type_data]
    room_type_counts = [item['total_bookings'] for item in room_type_data]

    # Booking Trends Over Time
    booking_trends = (
        Booking.objects.annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total_bookings=Count('id'))
        .order_by('month')
    )
    trend_labels = [item['month'].strftime('%Y-%m') for item in booking_trends]
    trend_counts = [item['total_bookings'] for item in booking_trends]

    context = {
        'city_labels': city_labels,
        'city_counts': city_counts,
        'room_type_labels': room_type_labels,
        'room_type_counts': room_type_counts,
        'trend_labels': trend_labels,
        'trend_counts': trend_counts,
    }

    return render(request, 'hotel/booking_dashboard.html', context)


from django.shortcuts import render
from django.http import HttpResponse
from .models import Booking, Hotel, RoomType
import openpyxl
from django.db.models import Sum

# Booking Summary Report
def booking_summary_report(request):
    bookings = Booking.objects.all()
    context = {
        'bookings': bookings
    }
    return render(request, 'reports/booking_summary_report.html', context)

def export_booking_summary_excel(request):
    bookings = Booking.objects.all()

    # Create a workbook and worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Booking Summary'

    # Header Row
    headers = ['Booking ID', 'Hotel', 'Room Type', 'Customer Name', 'Check-in Date', 'Check-out Date', 'Total Days', 'Total Amount', 'Payment Status']
    sheet.append(headers)

    # Data Rows
    for booking in bookings:
        sheet.append([
            booking.booking_id,
            booking.hotel.name if booking.hotel else 'N/A',
            booking.room_type.type if booking.room_type else 'N/A',
            booking.full_name,
            booking.check_in_date,
            booking.check_out_date,
            booking.total_days,
            booking.total,
            booking.payment_status
        ])

    # Download Response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=booking_summary_report.xlsx'
    workbook.save(response)
    return response

# Revenue Report
def revenue_report(request):
    revenues = Booking.objects.values('hotel__name').annotate(total_revenue=Sum('total'))
    context = {
        'revenues': revenues
    }
    return render(request, 'reports/revenue_report.html', context)

def export_revenue_report_excel(request):
    revenues = Booking.objects.values('hotel__name').annotate(total_revenue=Sum('total'))

    # Create a workbook and worksheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = 'Revenue Report'

    # Header Row
    headers = ['Hotel Name', 'Total Revenue']
    sheet.append(headers)

    # Data Rows
    for revenue in revenues:
        sheet.append([
            revenue['hotel__name'],
            revenue['total_revenue']
        ])

    # Download Response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=revenue_report.xlsx'
    workbook.save(response)
    return response


from django.shortcuts import render
import google.generativeai as genai

# Configure Gemini API with your API key
genai.configure(api_key="AIzaSyB-q88bHgiBT96U1_5IVPY-3RHHvZhiYGU")

def hotel_recommendation(request):
    recommendation = None

    if request.method == "POST":
        destination = request.POST['destination']
        room_type = request.POST['room_type']
        budget = request.POST['budget']  # Expecting a range like "100-300"
        amenities = request.POST['amenities']
        rating = request.POST['rating']  # Expecting a range like "4-5"
        hotel_category = request.POST['hotel_category']  # New field for Hotel Category

        # Constructing the prompt for the Gemini API
        user_input = f"""
        Destination City: {destination}
        Room Type Preference: {room_type}
        Budget Range: {budget}
        Preferred Amenities: {amenities}
        Rating Range: {rating}
        Hotel Category: {hotel_category}
        
        Please recommend suitable hotels along with:
        - Dining and Food Recommendations
        - Local Attractions and Activities
        - Present the output in bullet points for better readability
        """
        
        # Call the Gemini model
        model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(user_input)
        
        recommendation = response.text  # Fetch the recommendation result
    
    return render(request, 'hotel/hotel_recommendation.html', {'recommendation': recommendation})


OPENWEATHER_API_KEY = '55da2c2935f2507ee72a503eec6ab910'

def get_weather_data(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
            'icon': data['weather'][0]['icon']
        }
        
    return None

def get_weather_advice(description):
    if 'rain' in description:
        return "It's raining. Carry an umbrella and wear waterproof clothing."
    elif 'clear' in description:
        return "The weather is clear. Don't forget your sunglasses and sunscreen."
    elif 'cloud' in description:
        return "It's cloudy. You might want to carry a light jacket."
    elif 'snow' in description:
        return "Snowy weather ahead. Dress warmly and be cautious of slippery roads."
    else:
        return "Weather is moderate. Have a pleasant day!"
