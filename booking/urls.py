from django.urls import path
from booking import views

app_name="booking"

urlpatterns=[
    path("check_room_avaliability/",views.check_room_avaliability,name="check_room_avaliability"),
    path("add_to_selection/", views.add_to_selection, name="add_to_selection"),
    path('delete_selection/',views.delete_selection,name="delete_selection"),
]

