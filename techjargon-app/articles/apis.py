# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import pdb;
from rest_framework.renderers import JSONRenderer
from .models.article import Article
from .models.tag import Tag
from .models.content import Content
from .models.content_rating import ContentRating
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
import json
# tasks
from articles.tasks import article_tasks

# help : https://docs.djangoproject.com/en/1.11/ref/contrib/postgres/search/
def search(request):
	if request.method == 'POST':
		body_unicode = request.body.decode('utf-8')
		body = json.loads(body_unicode)
		_query = body['query']

		# advance search
		vector = SearchVector('title', weight='A') + SearchVector('tags__name', weight='B')
		search_query = SearchQuery(_query)

		articles = Article.objects.annotate(rank=SearchRank(vector, search_query)).filter(rank__gte=0.2).order_by('id').distinct('id')[:10]
		rank_sorted_articles = sorted(articles.all(), key=lambda a: a.rank)
		# articles = Article.objects.annotate(search=SearchVector('title', 'tags__name'),).filter(search=_query).distinct('id')
		_articles_seri = Article.ArticleSerializer(articles, many=True)
		return JsonResponse(_articles_seri.data, status=200, safe=False)
	else:
		return HttpResponse(status=404)


def check_article_exists(request):
	if request.method == 'POST':
		body_unicode = request.body.decode('utf-8')
		body = json.loads(body_unicode)
		_query = body['query']

		# advance search
		articles = Article.objects.filter(title__search=_query)

		_articles_seri = Article.ArticleSerializer(articles, many=True)
		return JsonResponse(_articles_seri.data, status=200, safe=False)
	else:
		return HttpResponse(status=404)
	

@login_required
def rate(request, article_id, content_id):
	_user = request.user
	# pdb.set_trace()
	if request.method == 'GET':
		try:

			_value = request.GET.get('v')
			# body_unicode = request.body.decode('utf-8')
			# body = json.loads(body_unicode)
			# _content_id = body['content_id']
			# _value = body['value']

			_content = Content.objects.get(pk=content_id)
			_rating, _created = ContentRating.objects.get_or_create(content_id=_content.id, user_id=_user.id)
			_rating.value = _value
			_rating.save()
			# average = processRating(_content)
			article_tasks.rate(_content.article.id)
		except Content.DoesNotExist:
			return HttpResponse(status=404)
			pass
		except IntegrityError as e:
			response = {
				'status': False,
				'message': e
			}
			return JsonResponse(response, status=500)
			pass
		else:
			# _todo_seri = ToDo.ToDoSerializer(_todo)
			response = {
				'status': True,
				'value': _value,
				'average': _content.article.rating,
				'count': _content.contentrating_set.count()
			}
			return JsonResponse(response, status=200)
	else:
		return HttpResponse(status=404)
