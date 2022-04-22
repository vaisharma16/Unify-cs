from django.db import models
from django.contrib.auth.models import User
from django.db.models.deletion import CASCADE
# from django.db.models.fields.files import ImageField
from django.urls import reverse, path, include
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.conf import settings
from autoslug import AutoSlugField
from django.dispatch import receiver



# def get_firstname(instance):
#      return instance.user.first_name
    
# def get_lastname(instance):
#     return instance.user.last_name

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete= models.CASCADE)
    # firstname = models.CharField(max_length= 100, blank = True, required = False)
    # lastname = models.CharField(max_length= 100, blank = True, required = False)
    Institute_Name = models.CharField(max_length= 100, blank = True, null = True, default = " ")
    Institute_Area = models.CharField(max_length= 100, blank = True, null = True, default = " ")
    phone = models.DecimalField(max_digits= 10, decimal_places= 0, blank = True, null = True, default = 0)
    image = models.ImageField(default = 'default.jpg', upload_to = 'profile_pics/')
    slug = AutoSlugField(populate_from = 'user')
    bio = models.CharField(max_length = 255, blank= True, null = True)
    friends = models.ManyToManyField("Profile", blank= True)

    def __str__(self):
        return str(self.user.username)

    def get_absolute_url(self):
        return f'/users/{self.slug}'

  
def create_profile(sender, instance, created, *args, **kwargs):
    if created:
        try:
            Profile.objects.create(user= instance)
        except:
            pass 

post_save.connect(create_profile, sender= settings.AUTH_USER_MODEL)

class FriendRequest(models.Model):
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name= 'to_user', on_delete= models.CASCADE)
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name= 'from_user', on_delete= models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add= True)

    def __str__(self):
        return f'From {self.from_user.username} to {self.to_user.username}'
