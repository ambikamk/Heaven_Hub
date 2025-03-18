from django.db import models
import shortuuid
from userauths.models import User
from shortuuid.django_fields import ShortUUIDField
from django.utils.text import slugify
from django.utils.html import mark_safe
from django_ckeditor_5.fields import CKEditor5Field
from taggit.managers import TaggableManager
from django.utils import timezone

HOTEL_STATUS=(
    ("Draft","Draft"),
    ("Disabled","Disabled"),
    ("Rejected","Rejected"),
    ("In Review","In Review"),
    ("Live","Live"),
)

ICON_TYPE=(
    ("Bootstrap Icons","Bootstrap Icons"),
    ("Fontawesome Icons","Fontawesome Icons"),
    ("Box Icons","Box Icons"),
    ("Remi Icons","Remi Icons"),
    ("Flat Icons","Flat Icons"),
)

PAYMENT_STATUS=(
    ("paid","paid"),
    ("pending","pending"),
    ("Processing","Processing"),
    ("cancelled","cancelled"),
    ("initiated","initiated"),
    ("failed","failed"),
    ("refunding","refunding"),
    ("refunded","refunded"),
     ("expired","expired"),
)

NOTIFICATION_TYPE= (
    ("Booking Confirmed","Booking Confirmed"),
    ("Booking Cancelled","Booking Cancelled")
)
RATING=(
    (1,"One Star"),
    (2,"Two Star"),
    (3,"Three Star"),
    (4,"Four Star"),
    (5,"Five Star"),
)


class Hotel(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name=models.CharField(max_length=100)
    description=CKEditor5Field(null=True,blank=True,config_name='extends')
    image=models.FileField(upload_to="hotel_gallery")
    address=models.CharField(max_length=200)
    mobile=models.CharField(max_length=200)
    email=models.EmailField(max_length=100)
    status=models.CharField(max_length=20,choices=HOTEL_STATUS,default="Live")
    tags=TaggableManager(blank=True)
    views=models.IntegerField(default=0)
    featured=models.BooleanField(default=False)
    hid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')
    slug=models.SlugField(unique=True)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def save(self,*args,**kwargs):
        if self.slug=="" or self.slug==None:
            uuid_key=shortuuid.uuid()
            uniqueid=uuid_key[:-4]
            self.slug=slugify(self.name) + "-" + str(uniqueid.lower())

        super(Hotel,self).save(*args,**kwargs)

    def thumbnail(self):
        return mark_safe("<img src='%s' width='50' height='50' style='object-fit:cover; border-radius:6px;' />" %(self.image.url))
    
    def hotel_gallery(self):
        return HotelGallery.objects.filter(hotel=self)
    
    def hotel_room_types(self):
        return RoomType.objects.filter(hotel=self)
    def average_rating(self):
        average_rating=Review.objects.filter(hotel=self).aggregate(avg_rating=models.Avg("rating"))
        return average_rating['avg_rating']
    def rating_count(self):
        return Review.objects.filter(hotel=self).count()


class HotelGallery(models.Model):
    hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE)
    image=models.FileField(upload_to="hotel_gallery")
    hgid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')

    def __str__(self):
        return str(self.hotel.name)
                   

    class Meta:
        verbose_name_plural="Hotel Gallery"

class HotelFeatures(models.Model):
    hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE)
    icon_type=models.CharField(max_length=100,null=True,blank=True,choices=ICON_TYPE)
    icon =models.CharField(max_length=100,null=True,blank=True)
    name=models.CharField(max_length=100,null=True,blank=True)
    def __str__(self):
        return str(self.name)
    
    class Meta:
        verbose_name_plural="Hotel Features"

class HotelFaqs(models.Model):
    hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE)
    question=models.CharField(max_length=1000)
    answer=models.CharField(max_length=1000,null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return str(self.question)
    
    class Meta:
        verbose_name_plural="Hotel FAQs"

class RoomType(models.Model):
    hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE)
    type=models.CharField(max_length=10)
    price=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    number_of_beds=models.PositiveIntegerField(default=0)
    room_capacity=models.PositiveIntegerField(default=0)
    rtid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')
    slug=models.SlugField(unique=True)
    date=models.DateTimeField(auto_now_add=True)
    
   

    def __str__(self):
        return f"{self.type} - {self.hotel.name} - {self.price}"
    
   
    class Meta:
        verbose_name_plural="Room Type"

    def rooms_count(self):
        Room.objects.filter(room_type=self).count()

    def save(self,*args,**kwargs):
        if self.slug=="" or self.slug==None:
            uuid_key=shortuuid.uuid()
            uniqueid=uuid_key[:-4]
            self.slug=slugify(self.name) + "-" + str(uniqueid.lower())

        super(RoomType,self).save(*args,**kwargs)

class Room(models.Model):
    hotel=models.ForeignKey(Hotel,on_delete=models.CASCADE)
    room_type=models.ForeignKey(RoomType,on_delete=models.CASCADE)
    room_number=models.CharField(max_length=1000)
    is_avaliable=models.BooleanField(default=True)
    rtid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')
    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.room_type.type} - {self.hotel.name} "
    
   
    class Meta:
        verbose_name_plural="Rooms"

    def price(self):
        return self.room_type.price
    
    def number_of_beds(self):
        return self.room_type.number_of_beds
    
class Booking(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    payment_status=models.CharField(max_length=100,choices=PAYMENT_STATUS)
    coupons = models.ManyToManyField("hotel.Coupon",blank=True)
    full_name=models.CharField(max_length=1000)
    email=models.EmailField(max_length=1000)
    phone=models.CharField(max_length=1000)
    hotel=models.ForeignKey(Hotel,on_delete=models.SET_NULL,null=True,blank=True)
    room_type=models.ForeignKey(RoomType,on_delete=models.SET_NULL,null=True,blank=True)
    room=models.ManyToManyField(Room)
    before_discount=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    total=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    saved=models.DecimalField(max_digits=12,decimal_places=2,default=0.00)
    check_in_date=models.DateField()
    check_out_date=models.DateField()
    total_days=models.PositiveIntegerField(default=0)
    num_adults=models.PositiveIntegerField(default=1)
    num_children=models.PositiveIntegerField(default=0)

    checked_in=models.BooleanField(default=False)
    checked_out=models.BooleanField(default=False)

    is_active=models.BooleanField(default=False)

    checked_in_tracker=models.BooleanField(default=False)
    checked_out_tracker=models.BooleanField(default=False)

    bid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')
    date=models.DateTimeField(auto_now_add=True)
    stripe_payment_intent = models.CharField(max_length=1000,null=True,blank=True)
    success_id=ShortUUIDField(length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')
    booking_id=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')
    is_cancelled = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.booking_id}"
    
    def rooms(self):
        return self.room.all().count()
    
class ActivityLog(models.Model):
    booking=models.ForeignKey(Booking,on_delete=models.CASCADE)
    guess_out=models.DateTimeField()
    guess_in=models.DateTimeField()
    description=models.TextField(null=True,blank=True)
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.booking}"
    
class staffOnDuty(models.Model):
    booking=models.ForeignKey(Booking,on_delete=models.CASCADE)
    staff_id=models.CharField(max_length=1000,null=True,blank=True)

    date=models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.staff_id}"

class Coupon(models.Model):
    code=models.CharField(max_length=1000)
    type=models.CharField(max_length=100,default="Percentage")
    discount=models.IntegerField(default=1)
    redemptions=models.IntegerField(default=0)
    date=models.DateTimeField(auto_now_add=True)
    active=models.BooleanField(default=True)
    valid_from=models.DateTimeField()
    valid_to=models.DateTimeField()
    cid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')

    def __str__(self):
        return f"{self.code}"

class Notification(models.Model):
      user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
      booking=models.ForeignKey(Booking,on_delete=models.SET_NULL,null=True,blank=True)
      type=models.CharField(max_length=100,choices=NOTIFICATION_TYPE)
      seen=models.BooleanField(default=True)
      date=models.DateTimeField(auto_now_add=True)

      def __str__(self):
        try:
          return f"{self.user.username} - {self.booking.booking_id}"
        except AttributeError:
          return "Incomplete Notification"
        
class Bookmark(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    hotel=models.ForeignKey(Hotel,on_delete=models.SET_NULL,null=True,blank=True)
    bid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.hotel.name}"
    
class Review(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    hotel=models.ForeignKey(Hotel,on_delete=models.SET_NULL,null=True,blank=True)
    review = models.TextField(null=True,blank=True)
    reply = models.TextField(null=True,blank=True)
    rating=models.PositiveIntegerField(default=None,choices=RATING)
    active=models.BooleanField(default=False)
    bid=ShortUUIDField(unique=True,length=10,max_length=20,alphabet='abcdefghijklmnopqrstuvwxyz')
    date=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return f"{self.user.username} - {self.hotel.name} - {self.rating} Star"
        except AttributeError:
            return "Incomplete Review"


class Blog(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    


    


      



# Create your models here.
