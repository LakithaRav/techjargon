from __future__ import absolute_import, unicode_literals
from celery import shared_task
# models
from articles.models.article import Article
from articles.models.content_rating import ContentRating

@shared_task
def test():
    return True


@shared_task
def rate(article_id):
    flag = False
    message = []
    try:
        article = Article.objects.get(pk=article_id)
        if article is not None:
            ratings = ContentRating.objects.filter(content_id__in=article.content_set.values('id')).order_by('user_id', '-id').distinct('user_id')
            _total = 0
            for rating in ratings:
                _total += rating.value

            _average = _total / ratings.count()
            article.rating = _average
            article.save()
        else:
            message.append("article not found")

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("ratings updated")
        flag = True

        return flag
