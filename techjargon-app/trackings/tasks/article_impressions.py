from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime, timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
import pdb
from datetime import datetime, timedelta, timezone
# models
from trackings.models.impression import Impression
from articles.models.article import Article
from django.contrib.auth.models import User
from authors.models.user_tag import UserTag

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


# @shared_task
# def suggest_user_tags():
#     flag = False
#
#     _preference = UserTag.PREFERENCE_TYPE[0][0]
#     _source = UserTag.SOURCE_TYPE[0][0]
#     try:
#         users = User.objects.filter(is_staff=False, is_active=True)
#         for user in users:
#             # UserTag.objects.filter(user=user, preferece=_preference, source=_source).delete()
#             impressions = Impression.objects.values('object_id').annotate(count=Count('object_id')).filter(user_id=user.id, content_type_id=ContentType.objects.get_for_model(Article).id).order_by('-count')[:5]
#             for impression in impressions:
#                 article = Article.objects.get(pk=impression['object_id'])
#                 tags = article.tags.order_by('-weight')[:5]
#                 for tag in tags:
#                     utag, created = UserTag.objects.get_or_create(preferece=_preference, source=_source, tag_id=tag.id, user_id=user.id)
#     except Exception as e:
#         flag = False
#     else:
#         flag = True
#
#     return flag

@shared_task
def suggest_user_tags():
    flag = False

    _preference = UserTag.PREFERENCE_TYPE[0][0]
    _source = UserTag.SOURCE_TYPE[0][0]
    _today = datetime.now().replace(tzinfo=timezone.utc)
    _before_day = _today - timedelta(days=30)
    try:
        users = User.objects.filter(is_staff=False, is_active=True)
        for user in users:
            # UserTag.objects.filter(user=user, preferece=_preference, source=_source).delete()
            impressions = Impression.objects.values('object_id').annotate(count=Count('object_id')).filter(user_id=user.id, content_type_id=ContentType.objects.get_for_model(Article).id, created_at__lte=_today, created_at__gt=_before_day).order_by('-count')
            article_ids = []
            for impression in impressions:
                article_ids.append(impression['object_id'])

            articles = Article.objects.filter(pk__in=article_ids).order_by('-rating', '-views')[:10]
            for article in articles:
                tags = article.tags.order_by('-weight')[:5]
                for tag in tags:
                    utag, created = UserTag.objects.get_or_create(preferece=_preference, source=_source, tag_id=tag.id, user_id=user.id)

    except Exception as e:
        flag = False
    else:
        flag = True

    return flag

# Impression.objects.values('content_type_id', 'object_id').annotate(count=Count('object_id')).order_by('-count')[0]['count']
# Article.objects.filter(pk=1).aggregate(Count('impressions'))
