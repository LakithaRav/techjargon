from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers
from datetime import datetime, timedelta


# Create your models here.
class Author(models.Model):
    # choices
    ROLE_TYPE = (
        (0, "Contributor"),
        (1, "Author"),
    )
    _DEFAULT_TYPE = 0

    role = models.PositiveSmallIntegerField(choices=ROLE_TYPE, default=_DEFAULT_TYPE)
    profil_pic = models.ImageField(upload_to='uploads/%Y/%m/%d/', max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    # relations
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

    class AuthorSerializer(serializers.Serializer):
        class UserSerializer(serializers.Serializer):
            id = serializers.IntegerField()
            username = serializers.CharField(max_length=300)

        id = serializers.IntegerField()
        user = UserSerializer()
        role_value = serializers.CharField(max_length=300)

    # public

    def role_value(self):
        _enum = self.ROLE_TYPE[self.role]
        return _enum[1]
