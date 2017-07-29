from django.db import models
from datetime import datetime
from .content import Content
from django.contrib.auth.models import User

# Create your models here.
class ContentRating(models.Model):
    value = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    # relations
    content = models.ForeignKey(Content, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(User, null=False)

    class Meta:
    	ordering = ['id']
