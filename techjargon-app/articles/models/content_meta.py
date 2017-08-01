from django.db import models
from datetime import datetime
from .content import Content


# Create your models here.
class ContentMeta(models.Model):
    name = models.CharField(max_length=100)
    data = models.TextField(null=True)

    # relations
    content = models.ForeignKey(Content, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.content.article.title, self.name)

    class Meta:
    	ordering = ['id']
