# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import pdb;
from rest_framework.renderers import JSONRenderer
from .models.article import Article
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