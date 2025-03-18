from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from django.http import JsonResponse
from hotel.models import Hotel,Booking,ActivityLog, HotelGallery,staffOnDuty,RoomType,Room,Coupon,HotelFeatures,HotelFaqs,Notification,Bookmark,Review
from userauths.models import Profile
from userauths.forms import UserUpateForm,ProfileUpdateForm

@login_required
def dashboard(request):
    profile= Profile.objects.get(user=request.user)
    bookings=Booking.objects.filter(user=request.user,payment_status="paid")
    total_spent=Booking.objects.filter(user=request.user,payment_status="paid").aggregate(amount=models.Sum("total"))
    context={
        "bookings":bookings,
        "total_spent":total_spent,
        "Profile":profile,
        
    }
    return render(request,"user_dashboard/dashboard.html",context)



@login_required
def bookings(request):
    profile= Profile.objects.get(user=request.user)
    bookings=Booking.objects.filter(user=request.user,payment_status="paid")
    context={
        "bookings":bookings,
        "Profile":profile,
        
    }
    return render(request,"user_dashboard/bookings.html",context)

@login_required
def booking_detail(request,booking_id):
    profile= Profile.objects.get(user=request.user)
    booking = Booking.objects.get(booking_id=booking_id,user=request.user,payment_status="paid")
    context={
        "booking":booking,
        "Profile":profile,
    }
    return render(request,"user_dashboard/booking_detail.html",context)


@login_required
def notifications(request):
    profile= Profile.objects.get(user=request.user)
    notifications = Notification.objects.filter(user=request.user,seen=False)
    context={
        "notifications":notifications,
        "Profile":profile,
    }
    return render(request,"user_dashboard/notifications.html",context)


def notification_mark_as_seen(request,id):
    noti = Notification.objects.get(id=id)
    noti.seen=True
    noti.save()
    messages.success(request,"Notification Seen")
    return redirect("user_dashboard:notifications")

@login_required
def wallet(request):
    profile= Profile.objects.get(user=request.user)
    bookings=Booking.objects.filter(user=request.user,payment_status="paid")
    total_spent=Booking.objects.filter(user=request.user,payment_status="paid").aggregate(amount=models.Sum("total"))
    wallet_balance=request.user.profile.wallet
    context={
        "bookings":bookings,
        "total_spent":total_spent,
        "wallet_balance":wallet_balance,
        "Profile":profile,
    }
    return render(request,"user_dashboard/wallet.html",context)


@login_required
def bookmark(request):
    profile= Profile.objects.get(user=request.user)
    bookmark=Bookmark.objects.filter(user=request.user)
    
    return render(request,"user_dashboard/bookmark.html",{"bookmark":bookmark,"Profile":profile})

def delete_bookmark(request,bid):
    bookmark=Bookmark.objects.get(bid=bid)
    bookmark.delete()
    messages.success(request,"Bookmark Deleted")
    return redirect("user_dashboard:bookmark")

def add_to_bookmark(request):
    id = request.GET['id']
    hotel=Hotel.objects.get(id=id)
    if request.user.is_authenticated:
        bookmark=Bookmark.objects.filter(user=request.user,hotel=hotel)
        if bookmark.exists():
            bookmark=Bookmark.objects.get(user=request.user,hotel=hotel)
            bookmark.delete()
            return JsonResponse({"data":"Bookmark deleted","icon":"success"})
        else:
            Bookmark.objects.create(user=request.user,hotel=hotel)
            return JsonResponse({"data":"Hotel Bookmarked","icon":"success"})
        
    else:
        return JsonResponse({"data":"Login to bookmark hotel","icon":"warning"})
    
@login_required
def profile(request):
    profile= Profile.objects.get(user=request.user)

    if request.method == "POST":
        u_form = UserUpateForm(request.POST,instance=request.user)
        p_form = ProfileUpdateForm(request.POST,request.FILES,instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()

            messages.success(request,"Profile updated successfully")
            return redirect("user_dashboard:profile")
    
    else:
        u_form = UserUpateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)


    context={
        "Profile":profile,
        "u_form":u_form,
        "p_form":p_form,
    }
    return render(request,"user_dashboard/profile.html",context)

@login_required
def password_changed(request):
   
    return render(request,"user_dashboard/password_changed.html")


def add_review(request):
    
    id = request.GET['id']
    review = request.GET['review']
    rating = request.GET['rating']

    hotel = Hotel.objects.get(id=id)
    review_check = Review.objects.filter(user=request.user,hotel=hotel)

    if review_check.exists():
        return JsonResponse({"data":"Review already exists","icon":"warning"})
    else:
        Review.objects.create(
            user=request.user,
            rating=rating,
            review=review,
            hotel=hotel
        )
        return JsonResponse({"data":"Review Submitted","icon":"success"})


from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse

@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(
        Booking, booking_id=booking_id, user=request.user, payment_status="paid", is_cancelled=False
    )

    if request.method == "POST":
        # Mark the booking as cancelled
        booking.is_cancelled = True
        booking.payment_status = "Cancelled"
        booking.save()

        # Mark the rooms as available
        for room in booking.room.all():
            room.is_avaliable = True
            room.save()

        # Send cancellation email
        context = {
            "full_name": booking.full_name,
            "hotel": booking.hotel.name,
            "room_type": booking.room_type.type,
            "check_in_date": booking.check_in_date,
            "check_out_date": booking.check_out_date,
            "total": booking.total,
        }
        subject = "Booking Cancelled Successfully"
        html_message = render_to_string("user_dashboard/booking_cancelled_email.html", context)

        send_mail(
            subject,
            "Your booking has been successfully cancelled.",
            "mkambika287@gmail.com",
            [booking.email],
            fail_silently=False,
            html_message=html_message
        )

        messages.success(
            request,
            "Your booking has been cancelled successfully. Refund will be processed within 48 hours."
        )
        return redirect("user_dashboard:dashboard")  # Redirect to the bookings list page

    return render(request, "user_dashboard/cancel_booking_confirmation.html", {"booking": booking})



        




        






# Create your views here.
