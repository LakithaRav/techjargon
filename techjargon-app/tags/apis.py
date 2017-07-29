# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
import pdb;
from rest_framework.renderers import JSONRenderer
from .models.tag import Tag
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
import json
# tasks

def search(request):
	if request.method == 'POST':
		body_unicode = request.body.decode('utf-8')
		body = json.loads(body_unicode)
		_query = body['query']

		# advance search
		tags = Tag.objects.filter(name__search=_query)
		# rank_sorted_articles = sorted(articles.all(), key=lambda a: a.views)

		_tags_seri = Tag.TagSerializer(tags, many=True)
		return JsonResponse(_tags_seri.data, status=200, safe=False)
	else:
		return HttpResponse(status=404)