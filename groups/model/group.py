# from django.contrib.auth.models import Group
from django.db import models
# from django.contrib.auth.models import User
from django.conf import settings
import random

class CustomGroup(models.Model):
    ACCESS_CHOICES = [
        ("1", "Private"),
        ("2", "Public"),
    ]
    name = models.CharField(max_length=255)
    access = models.CharField(max_length=50,null=True,blank=True,choices=ACCESS_CHOICES)
    thumbnail = models.ImageField(upload_to='groups/', blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_groups')
    code = models.CharField(max_length=10,unique=True, blank=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.code:  # Only generate a code if it doesn't already exist
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_unique_code():
        while True:
            code = f"{random.randint(100000, 999999)}"
            if not CustomGroup.objects.filter(code=code).exists():
                return code

class photo_group(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    photo_name = models.CharField(max_length=255,blank=True)
    image = models.BinaryField(editable=True,blank=True,null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.photo_name or f"Photo {self.id}"
    

class GroupMember(models.Model):
    group = models.ForeignKey(CustomGroup, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  
    role = models.CharField(max_length=50,null=True,blank=True)
    user_verified = models.BooleanField(default=False) 
    joined_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.user} - {self.group.name}"
