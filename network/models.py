from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=64, blank=True)
    following = models.ManyToManyField('self', symmetrical=False, related_name='followers')

    def __str__(self):
        return self.username

class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')  #link post to the user
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True) #automatically sets the time
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    
    def __str__(self):
        return f"{self.user.username} {self.body[:30]} {self.likes}"