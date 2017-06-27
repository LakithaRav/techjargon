from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
from rest_framework import serializers
from django.contrib.auth.models import User


# Create your models here.
class Impression(models.Model):

    class Meta:
        ordering = ['-created_at']


    ip_address = models.GenericIPAddressField(protocol='both', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    # polymorphic relations
    # ref https://docs.djangoproject.com/en/1.11/ref/contrib/contenttypes/#generic-relations
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    #relations
    user = models.ForeignKey(User, blank=True, null=True, default=-1)
