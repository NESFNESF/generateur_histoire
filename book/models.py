from django.contrib.auth.models import User
from django.db import models
from django.conf import settings


class Image(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    buttons = models.TextField(blank=True, null=True)
    imageUrl = models.TextField(blank=True, null=True)
    buttonMessageId = models.TextField(blank=True, null=True)
    originatingMessageId = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    
        
    class Meta:
        ordering=['created_at']

    def __str__(self):
        return self.buttonMessageId
    
class History(models.Model):
    content = models.TextField(blank=True, null=True) #sauvegarde le JSON des histoires
    created_at = models.DateTimeField(auto_now_add=True) # conserve la date de creation des histoires
    class Meta:
        ordering=['created_at']

    def __str__(self):
        return self.content
