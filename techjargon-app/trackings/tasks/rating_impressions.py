from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime, timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count
import pdb
from datetime import datetime, timedelta, timezone
# models
from trackings.models.impression import Impression
from articles.models.content_rating import ContentRating
from django.contrib.auth.models import User
from authors.models.user_tag import UserTag

@shared_task
def suggest_user_tags():
    flag = False

    _preference = UserTag.PREFERENCE_TYPE[0][0]
    _source = UserTag.SOURCE_TYPE[2][0]
    _today = datetime.now().replace(tzinfo=timezone.utc)
    _before_day = _today - timedelta(days=30)
    # pdb.set_trace()
    try:
        users = User.objects.filter(is_staff=False, is_active=True)
        for user in users:
            # UserTag.objects.filter(user=user, preferece=_preference, source=_source).delete()
            ratings = ContentRating.objects.filter(user_id=user.id, updated_at__lte=_today, updated_at__gt=_before_day).order_by('-value')
            for rating in ratings:
                tags = rating.content.article.tags.order_by('-weight')[:5]
                for tag in tags:
                    utag, created = UserTag.objects.get_or_create(preferece=_preference, source=_source, tag_id=tag.id, user_id=user.id)

    except Exception as e:
        flag = False
    else:
        flag = True

    return flag
