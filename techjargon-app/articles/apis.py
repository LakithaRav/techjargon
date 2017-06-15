# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import pdb;
from rest_framework.renderers import JSONRenderer
from .models.article import Article
from .models.content import Content
from .models.content_rating import ContentRating
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
import json


# help : https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/search/
def search(request):
	if request.method == 'POST':
		body_unicode = request.body.decode('utf-8')
		body = json.loads(body_unicode)
		_query = body['query']

		# advance search
		vector = SearchVector('title', weight='A') + SearchVector('tags__name', weight='B')
		search_query = SearchQuery(_query)

		articles = Article.objects.annotate(rank=SearchRank(vector, search_query)).filter(rank__gte=0.2).order_by('id').distinct('id')
		rank_sorted_articles = sorted(articles.all(), key=lambda a: a.rank)
		# articles = Article.objects.annotate(search=SearchVector('title', 'tags__name'),).filter(search=_query).distinct('id')
		_articles_seri = Article.ArticleSerializer(articles, many=True)
		return JsonResponse(_articles_seri.data, status=200, safe=False)
	else:
		return HttpResponse(status=404)


@login_required
def rate(request):
	_user = request.user
	# pdb.set_trace()
	if request.method == 'POST':
		try:
			body_unicode = request.body.decode('utf-8')
			body = json.loads(body_unicode)
			_content_id = body['content_id']
			_value = body['value']

			_content = Content.objects.get(pk=_content_id)
			_rating, _created = ContentRating.objects.get_or_create(content_id=_content_id, owner_id=_user.author.id)
			_rating.value = _value
			_rating.save()
			average = processRating(_content)
		except Content.DoesNotExist:
			return HttpResponse(status=404)
			pass
		except IntegrityError as e:
			_message.append(e)
			pass
		else:
			# _todo_seri = ToDo.ToDoSerializer(_todo)
			response = {
				'status': True,
				'value': _value,
				'average': average,
				'count': _content.contentrating_set.count()
			}
			return JsonResponse(response, status=200)
	else:
		return HttpResponse(status=404)


# private
def processRating(content):
	ratings = content.contentrating_set.all()
	_total = 0
	for rating in ratings:
		_total += rating.value

	_average = _total / ratings.count()
	content.article.rating = _average
	content.article.save()
	return _average
