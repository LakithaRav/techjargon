from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime, timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
import pdb
from datetime import datetime, timedelta, timezone
# models
from trackings.models.impression import Impression
from django.contrib.auth.models import User
from articles.models.tag import Tag
from authors.models.user_tag import UserTag

@shared_task
def add(tag_id, user_id, request_ip):
    flag = False
    message = []
    try:
        # pdb.set_trace()
        tag = Tag.objects.get(pk=tag_id)
        if tag is not None:
            nview = Impression(ip_address=request_ip, content_object=tag, user_id=user_id)
            nview.save()
            Tag.objects.filter(id=tag.id).update(views=tag.impressions.count())
        else:
            message.append("tag not found")

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("tag log added")
        flag = True

    return flag


@shared_task
def suggest_user_tags():
    flag = False
    # pdb.set_trace()
    _preference = UserTag.PREFERENCE_TYPE[0][0]
    _source = UserTag.SOURCE_TYPE[1][0]
    _today = datetime.now().replace(tzinfo=timezone.utc)
    _before_day = _today - timedelta(days=30)
    try:
        users = User.objects.filter(is_staff=False, is_active=True)
        for user in users:
            impressions = Impression.objects.values('object_id').annotate(count=Count('object_id')).filter(user_id=user.id, content_type_id=ContentType.objects.get_for_model(Tag).id, created_at__lte=_today, created_at__gt=_before_day).order_by('-count')[:10]
            # impressions = Impression.objects.values('object_id').annotate(count=Count('object_id')).filter(user_id=user.id, content_type_id=ContentType.objects.get_for_model(Tag).id).order_by('-count')[:5]
            tag_ids = []
            for impression in impressions:
                tag_ids.append(impression['object_id'])

            tags = Tag.objects.filter(pk__in=tag_ids).order_by('-weight')[:5]
            for tag in tags:
                utag, created = UserTag.objects.get_or_create(preferece=_preference, source=_source, tag_id=tag.id, user_id=user.id)
    except Exception as e:
        flag = False
    else:
        flag = True

    return flag
