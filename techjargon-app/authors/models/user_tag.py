from django.db import models
from rest_framework import serializers
from datetime import datetime, timedelta
# models
from django.contrib.auth.models import User
from tags.models.tag import Tag

# Create your models here.
class UserTag(models.Model):
    # choices
    PREFERENCE_TYPE = (
        (1, "System"),
        (2, "User"),
    )
    _PREF_DEFAULT_TYPE = 1

    SOURCE_TYPE = (
        (1, "articles"),
        (2, "Tags"),
        (3, "Ratings"),
    )
    _SRC_DEFAULT_TYPE = 2

    preferece = models.PositiveSmallIntegerField(choices=PREFERENCE_TYPE, default=_PREF_DEFAULT_TYPE)
    source = models.PositiveSmallIntegerField(choices=SOURCE_TYPE, default=_SRC_DEFAULT_TYPE)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)

    # relations
    tag = models.ForeignKey(Tag, null=False)
    user = models.ForeignKey(User, null=False)

    def __str__(self):
        return self.tag.name

    # public

    def preferece_str(self):
        _enum = self.PREFERENCE_TYPE[self.preferece]
        return _enum[1]
