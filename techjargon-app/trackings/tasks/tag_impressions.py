from __future__ import absolute_import, unicode_literals
from celery import shared_task
from datetime import datetime, timezone
# models
from trackings.models.impression import Impression
from articles.models.tag import Tag

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
