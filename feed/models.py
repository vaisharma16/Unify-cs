from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
# Create your models here.

# get url for saving the users files in the media folder
def get_path(instance, filename):
    return f'posts/{instance.username}/{filename}'

class Post(models.Model):
    description = models.CharField(max_length = 255, blank = True)
    username = models.ForeignKey(User, on_delete = models.CASCADE)
    pic = models.ImageField(upload_to = get_path)
    date_posted = models.DateTimeField(default = timezone.now)
    tags = models.CharField(max_length = 100, blank = True)

    def __str__(self):
        return self.description
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs = {'pk':self.pk})

class Comments(models.Model):
    post = models.ForeignKey(Post, related_name = 'details', on_delete = models.CASCADE)
    username = models.ForeignKey(User, related_name = 'details', on_delete = models.CASCADE)
    comment = models.CharField(max_length = 255)
    comment_date = models.DateTimeField(default = timezone.now)

class Like(models.Model):
    post = models.ForeignKey(Post, related_name = 'likes', on_delete = models.CASCADE)
    user = models.ForeignKey(User, related_name = 'likes', on_delete = models.CASCADE)
