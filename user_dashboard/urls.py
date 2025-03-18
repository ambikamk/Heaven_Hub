from django.contrib import admin
from django.urls import path,include
from user_dashboard import views
from django.contrib.auth import views as auth_view

app_name="user_dashboard"

urlpatterns = [
    #path('admin/', admin.site.urls),
    path("",views.dashboard,name="dashboard"),
    path("booking-detail/<booking_id>/",views.booking_detail,name="booking_detail"),
    path("bookings/",views.bookings,name="bookings"),
    path("notifications/",views.notifications,name="notifications"),
    path("notification_mark_as_seen/<id>/",views.notification_mark_as_seen,name="notification_mark_as_seen"),
    path("wallet/",views.wallet,name="wallet"),
    path("bookmark/",views.bookmark,name="bookmark"),
    path("delete_bookmark/<bid>/",views.delete_bookmark,name="delete_bookmark"),
    path("add_to_bookmark/",views.add_to_bookmark,name="add_to_bookmark"),
    path("profile/",views.profile,name="profile"),
    path("change-password/",auth_view.PasswordChangeView.as_view(template_name="user_dashboard/password-reset/change-password.html",success_url="/dashboard/password-changed/"),name="change_password"),
    path("password-changed/",views.password_changed,name="password_changed"),
    path("add_review/",views.add_review,name="add_review"),
    path("bookings/<str:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),

]