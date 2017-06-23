from __future__ import absolute_import, unicode_literals
from celery import shared_task
from articles.models.article_view import ArticleView

@shared_task
def test():
    return True
