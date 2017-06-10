from django.db import models
from datetime import datetime
from django.db.models import F


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True, max_length=150, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated_at = models.DateTimeField(auto_now_add=True)

    # private

    def increase_weight(self, type):
        if type == 0:
            # self.weight = F('weight') + 0.05
            Tag.objects.filter(id=self.id).update(weight=F('weight') + 0.05)
        elif type == 1:
            # self.weight = F('weight') + 0.01
            Tag.objects.filter(id=self.id).update(weight=F('weight') + 0.01)

        self.save()
