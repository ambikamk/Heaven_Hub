from django.contrib import admin
from django.urls import path,include
from hotel import views

app_name = 'hotel'

urlpatterns = [
    #path('admin/', admin.site.urls),
    path("",views.index,name="index"),
    path("about/",views.about,name="about"),
    path("services/",views.services,name="services"),
    path("packages/",views.packages,name="packages"),
    path("blog/",views.blog,name="blog"),
    path("contact/",views.contact,name="contact"),
    path("detail/<slug>/", views.hotel_detail, name="hotel_detail"),
    path("detail/<slug:slug>/room_type/<slug:rt_slug>/",views.room_type_detail,name="room_type_detail"),
    path("selected_rooms/",views.selected_rooms,name="selected_rooms"),
    path("checkout/<booking_id>/",views.checkout,name="checkout"),
    path("update_room_status/",views.update_room_status,name="update_room_status"),
    path("api/create_checkout_session/<booking_id>/",views.create_checkout_session,name="api_checkout_session"),
    path("success/<booking_id>/",views.payment_success,name="success"),
    path("failed/<booking_id>/",views.payment_failed,name="failed"),
    path('booking/<str:booking_id>/invoice/', views.generate_invoice, name='generate_invoice'),
    path('search/', views.search_hotels, name='search_hotels'),
    path('visualization/', views.booking_dashboard, name='booking_dashboard'),
    path('reports/booking-summary/', views.booking_summary_report, name='booking_summary_report'),
    path('reports/booking-summary/export/', views.export_booking_summary_excel, name='export_booking_summary_excel'),
    path('reports/revenue/', views.revenue_report, name='revenue_report'),
    path('reports/revenue/export/', views.export_revenue_report_excel, name='export_revenue_report_excel'),
    path('recommendations/', views.hotel_recommendation, name='hotel_recommendation'),

]