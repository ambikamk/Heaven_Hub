from django.contrib import admin

from hotel.models import Hotel,Booking,ActivityLog, HotelGallery,staffOnDuty,RoomType,Room,Coupon,HotelFeatures,HotelFaqs,Notification,Bookmark,Review,Blog,ContactMessage

class HotelGalleryInline(admin.TabularInline):
    model=HotelGallery

class HotelFeaturesInline(admin.TabularInline):  
    model = HotelFeatures

class RoomTypeInline(admin.TabularInline):
    model=RoomType

class RoomInline(admin.TabularInline):
    model=Room

class HotelFaqsInline(admin.TabularInline):
    model=HotelFaqs

class HotelAdmin(admin.ModelAdmin):
    inlines = [HotelGalleryInline,HotelFeaturesInline,RoomTypeInline,RoomInline,HotelFaqsInline]
    list_display = ['thumbnail','name','user','status']
    prepopulated_fields = {'slug':('name',)}


class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject','message','created_at')
    search_fields = ('name', 'email', 'subject')

admin.site.register(ContactMessage, ContactMessageAdmin)

admin.site.register(Hotel,HotelAdmin)
admin.site.register(Booking)
admin.site.register(ActivityLog)
admin.site.register(staffOnDuty)
admin.site.register(RoomType)
admin.site.register(Room)
admin.site.register(Coupon)
admin.site.register(Notification)
admin.site.register(Bookmark)
admin.site.register(Review)
admin.site.register(Blog)
    
# Register your models here.
