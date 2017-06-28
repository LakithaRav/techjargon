from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime, timezone
# models
from trackings.models.impression import Impression
from articles.models.article import Article

@shared_task
def add(article_id, user_id, request_ip):
    flag = False
    message = []
    try:
        # pdb.set_trace()
        article = Article.objects.get(pk=article_id)
        if article is not None:
            nview = Impression(ip_address=request_ip, content_object=article, user_id=user_id)
            nview.save()
            Article.objects.filter(id=article.id).update(views=article.impressions.count())
        else:
            message.append("article not found")

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("View log added")
        flag = True

    return flag

# Impression.objects.values('content_type_id', 'object_id').annotate(count=Count('object_id')).order_by('-count')[0]['count']
# Article.objects.filter(pk=1).aggregate(Count('impressions'))
