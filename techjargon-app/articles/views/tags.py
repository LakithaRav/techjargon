from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from articles.models.tag import Tag
from articles.models.article import Article
from articles.models.content import Content
import pdb;
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def detail(request, slug):

    _page = request.GET.get('page')

    _tag = get_object_or_404(Tag, slug=slug)
    _articles = Article.objects.filter(tags__slug=slug).order_by('-views')
    _new_articles = Article.objects.filter(tags__slug=slug).order_by('-created_at')[:5]

    # pagination
    paginator = Paginator(_articles, 5)

    try:
        _paginated_artciles = paginator.page(_page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _paginated_artciles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _paginated_artciles = paginator.page(paginator.num_pages)

    _ralated_tags = []
    for article in _articles:
        _ralated_tags = list(set(_ralated_tags) | set(article.tags.all()))

    _context = {
        'tag': _tag,
        'hit_count': _articles.count,
        'ralated_tags': _ralated_tags,
        'articles': _paginated_artciles,
        'new_articles': _new_articles,
        'full_url_path': request.build_absolute_uri()
    }

    # weghy
    _tag.increase_weight(0)

    return render(request, 'tags/detail.html', _context)
