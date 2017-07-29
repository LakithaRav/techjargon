from django.db import models
from django.contrib.auth.models import User
from rest_framework import serializers
from datetime import datetime, timedelta
from django.core import files
from io import BytesIO
import requests
import os


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

    def get_remote_file(self, url):
        url = url.replace('https://', 'http://', 1)
        resp = requests.get(url)
        if resp.status_code == requests.codes.ok:
            fp = BytesIO()
            fp.write(resp.content)
            file_name = os.path.basename(url)
            self.profil_pic.save(file_name, files.File(fp))
