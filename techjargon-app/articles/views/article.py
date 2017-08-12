from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.db import IntegrityError
from django.db.models import F
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.postgres.search import TrigramSimilarity
import operator
import hashlib
import pdb
from rest_framework.renderers import JSONRenderer
import json
# models
from authors.models.author import Author
from articles.models.article import Article
from articles.models.content import Content
from tags.models.tag import Tag
from articles.models.content_meta import ContentMeta
from articles.models.content_rating import ContentRating
from trackings.models.impression import Impression
from authors.models.user_tag import UserTag
# forms
from articles.forms.article import NewArticleForm
from articles.forms.article import UpdateArticleForm
# tasks
from trackings.tasks import article_impressions as impressions


# Create your views here.

def index(request):
    
    articles = []
    suggesting_articles = []
    page_meta = {
        'keywords': '',
        'articles': '',
        'suggesting_articles': '',
        'full_url_path': request.build_absolute_uri(),
    }

    if request.user.is_authenticated:
        articles = Article.objects.filter(status=Article.STATUS[1][0], in_home=True).order_by('-created_at')[:20]
        _sugg_tags = __get_suggetion_tags(request.user.id)
        suggesting_articles = Article.objects.filter(status=Article.STATUS[1][0], tags__pk__in=_sugg_tags).distinct('id').order_by('-id', '-created_at')[:20]
        suggesting_articles = sorted(suggesting_articles, key=operator.attrgetter('views', 'rating'), reverse=True)
    else:
        articles = Article.objects.filter(status=Article.STATUS[1][0], in_home=True).order_by('-views')[:20]
        _sugg_tags = __get_suggetion_tags(None)
        suggesting_articles = Article.objects.filter(status=Article.STATUS[1][0], tags__pk__in=_sugg_tags).distinct('id').order_by('-id', '-created_at')[:20]
        suggesting_articles = sorted(suggesting_articles, key=operator.attrgetter('views', 'rating'), reverse=True)

    for article in articles:
        page_meta['keywords'] += article.title + ','

    _articles_seri = Article.ArticleSerializer(articles, many=True)
    page_meta['articles'] = JSONRenderer().render(_articles_seri.data)

    _articles_seri = Article.ArticleSerializer(suggesting_articles, many=True)
    page_meta['suggesting_articles'] = JSONRenderer().render(_articles_seri.data)

    context = {
        'articles': articles,
        'suggesting_articles': suggesting_articles,
        'meta': page_meta,
    }

    return render(request, 'articles/index.html', context)

def search(request):
    # pdb.set_trace()
    _query = request.GET.get('q')
    _page = request.GET.get('page')
    # _page = int(_page)

    # advance search
    vector = SearchVector('title', weight='A') + SearchVector('tags__name', weight='B')
    search_query = SearchQuery(_query)
    trigram_similarity = TrigramSimilarity('title', _query) + TrigramSimilarity('tags__name', _query)

    _articles = Article.objects.annotate(rank=SearchRank(vector, search_query), similarity=trigram_similarity).filter(similarity__gt=0.3, status=Article.STATUS[1][0]).order_by('id', '-similarity').distinct('id')[:10]
    _tags = Tag.objects.filter(name__contains=_query).order_by('-weight')[:20]

    paginator = Paginator(_articles, 5)
    try:
        _paginated_artciles = paginator.page(_page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        _paginated_artciles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        _paginated_artciles = paginator.page(paginator.num_pages)

    _context = {
        'query': _query,
        'articles': _paginated_artciles,
        'tags': _tags,
        'cpage': _page
    }
    return render(request, 'articles/search.html', _context)

def detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    _tags = []
    for tag in article.tags.all():
        _tags.append(tag.id)

    action_ids = Article.objects.filter(tags__id__in=_tags, status=Article.STATUS[1][0]).exclude(id=article.id).distinct('id').values_list('id', flat=True)
    related_articles = Article.objects.filter(id__in=action_ids, status=Article.STATUS[1][0]).order_by('-tags__weight').order_by('-views')[:10]

    _total_ratings = ContentRating.objects.filter(content_id__in=article.content_set.values('id')).order_by('user_id', '-id').distinct('user_id').count()
    _my_rating = 0
    if hasattr(request.user, 'author'):
        try:
            _rating = ContentRating.objects.get(content_id=article.active_content().id, user_id=request.user.id)
            _my_rating = _rating.value
        except Author.DoesNotExist:
            _my_rating = -1
            pass
        except ContentRating.DoesNotExist:
            _my_rating = -1
            pass

    _context = {
        'article': article,
        'content': article.active_content,
        'related_articles': related_articles,
        'my_rating': _my_rating,
        'total_ratings': _total_ratings,
        'full_url_path': request.build_absolute_uri()
    }

    __add_view_log(request, article)

    return render(request, 'articles/detail.html', _context)

def network(request, slug):
    article = get_object_or_404(Article, slug=slug)

    connection_tree = []
    excludes = []
    excludes.append(article.id)
    connection_tree = __get_article_tree(article, connection_tree, excludes, 0)
    tree_data = json.dumps(connection_tree)

    _context = {
        'article': article,
        'content': article.active_content,
        'full_url_path': request.build_absolute_uri(),
        'relation_tree': tree_data
    }

    return render(request, 'articles/network.html', _context)

def history(request, slug, content_id):
    article = get_object_or_404(Article, slug=slug)
    content = Content.objects.get(pk=content_id)
    _context = {
        'article': article,
        'content': content
    }

    return render(request, 'articles/history.html', _context)

def about(request):
    _context = {
    }
    return render(request, 'about.html', _context)

@login_required
def add(request):
    if request.method == 'POST':
        # pdb.set_trace()
        _form = NewArticleForm(request.POST)
        if _form.is_valid():
            _user = request.user

            _metas = {
                'keys': _form.data.getlist('meta_keys'),
                'values': _form.data.getlist('meta_values')
            }
            flag, message, article = __save_article(_form.cleaned_data, _user, _metas)
            if flag:
                return HttpResponseRedirect('/article/%s' % (article.slug))
            else:
                _context = {
                    'form': _form,
                    'errors': message
                }
                return render(request, 'articles/add.html', _context)

        else:
            _context = {
                'form': _form
            }
            return render(request, 'articles/add.html', _context)
    else:
        _form = NewArticleForm()
        _context = {
            'form': _form
        }
        # pdb.set_trace()
        return render(request, 'articles/add.html', _context)

@login_required
def update(request, slug, article_id):
    _article = get_object_or_404(Article, id=article_id)

    # take current content hash
    _meta_keys = []
    _meta_values = []
    for meta in _article.active_content().contentmeta_set.all():
        _meta_keys.append(meta.name)
        _meta_values.append(meta.data)

    _hash = hashlib.md5(_article.active_content().body.encode())
    _hash.update(repr(_meta_keys).encode('utf-8'))
    _hash.update(repr(_meta_values).encode('utf-8'))

    _uform = UpdateArticleForm(request.POST or None, initial={'article_id': article_id, 'content': _article.active_content().body, 'tags': _article.tags_str(), 'content_hash': _hash.hexdigest()})
    # pdb.set_trace()
    if request.method == 'POST':
        if _uform.is_valid():
            _user = request.user
            _metas = {
                'keys': _uform.data.getlist('meta_keys'),
                'values': _uform.data.getlist('meta_values')
            }
            flag, message, article = __update_article(_uform.cleaned_data, _user, _article, _metas)
            if flag:
                return HttpResponseRedirect('/article/%s' % (article.slug))
            else:
                _context = {
                    'form': _form,
                    'errors': message
                }
                return render(request, 'articles/update.html', _context)

    _context = {
        'article': _article,
        'uform': _uform
    }
    return render(request, 'articles/update.html', _context)


# private
def __save_article(post, user, metas):
    flag = False
    message = []
    try:
        _slug = slugify(post['title'])
        _article = Article(title=post['title'], slug=_slug, status=Article._DEFAULT_STATUS)
        _content = Content(body=post['content'], status=Content._DEFAULT_STATUS, author=user.author)
        
        _article.save()

        article_tags = []
        _tags = post['tags']
        for _tag in _tags:
            tag, created = Tag.objects.get_or_create(name=_tag.lower(), slug=slugify(_tag))
            if not created:
                tag.increase_weight(1)
            _article.tags.add(tag)

        _content.article = _article
        _content.save()

        _key_index = 0
        for key in metas['keys']:
            _meta = ContentMeta(name=key, data=metas['values'][_key_index])
            _meta.content = _content
            _meta.save()
            _key_index += 1

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("Article created successfully")
        flag = True

    return flag, message, _article


def __update_article(post, user, article, metas):
    flag = False
    message = []
    try:

        article.tags.clear()

        article_tags = []
        _tags = post['tags']
        for _tag in _tags:
            tag, created = Tag.objects.get_or_create(name=_tag.lower(), slug=slugify(_tag))
            if not created:
                tag.increase_weight(1)
            article.tags.add(tag)

        # take current content hash
        _meta_keys = []
        _meta_values = []
        _key_index = 0
        for key in metas['keys']:
            _meta_keys.append(key)
            _meta_values.append(metas['values'][_key_index])

        _hash = hashlib.md5(post['content'].encode())
        _hash.update(repr(_meta_keys).encode('utf-8'))
        _hash.update(repr(_meta_values).encode('utf-8'))

        if _hash.hexdigest() != post['content_hash']:
            _content = Content(body=post['content'], status=Content._DEFAULT_STATUS, author=user.author)

            article.content_set.update(status=Content.STATUS[0][0])
            _content.article = article
            _content.save()

            _key_index = 0
            for key in metas['keys']:
                _meta = ContentMeta(name=key, data=metas['values'][_key_index])
                _meta.content = _content
                _meta.save()
                _key_index += 1

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("Content updated successfully")
        flag = True

    return flag, message, article


def __add_view_log(request, article):
    user_id = None
    if request.user.is_authenticated:
        user_id = request.user.id

    ip_address = __get_ip(request)
    # impressions.add.delay(article.id, user_id, request.META.get('REMOTE_ADDR'))
    impressions.add.delay(article.id, user_id, ip_address)

def __get_ip(request):
    """Returns the IP of the request, accounting for the possibility of being
    behind a proxy.
    """
    ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if ip:
        # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
        ip = ip.split(", ")[0]
    else:
        ip = request.META.get("REMOTE_ADDR", "")
    return ip


def __get_suggetion_tags(user_id):
    primary_tags = []
    optional_tags = []

    if user_id is not None:
        _article_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[0][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')[:10]
        _tags_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[1][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')[:10]
        _rating_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[2][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')[:10]
    else:
        _article_tags = UserTag.objects.filter(source=UserTag.SOURCE_TYPE[0][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')[:10]
        _tags_tags = UserTag.objects.filter(source=UserTag.SOURCE_TYPE[1][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')[:10]
        _rating_tags = UserTag.objects.filter(source=UserTag.SOURCE_TYPE[2][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')[:10]

    optional_tags += _article_tags
    optional_tags += _tags_tags
    optional_tags += _rating_tags

    # _article_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[0][0], preferece=UserTag.PREFERENCE_TYPE[1][0]).order_by('-created_at')
    # _tags_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[1][0], preferece=UserTag.PREFERENCE_TYPE[1][0]).order_by('-created_at')
    # _rating_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[2][0], preferece=UserTag.PREFERENCE_TYPE[1][0]).order_by('-created_at')

    # primary_tags += _article_tags
    # primary_tags += _tags_tags
    # primary_tags += _rating_tags

    tags = []
    for tag in optional_tags:
        tags.append(tag.tag_id)

    return tags


def __get_article_tree(article, collection, excludes, level):  
    _tags = []
    for tag in article.tags.all():
        _tags.append(tag.id)

    action_ids = Article.objects.filter(tags__id__in=_tags, status=Article.STATUS[1][0]).exclude(id__in=excludes).distinct('id').values_list('id', flat=True)
    related_articles = Article.objects.filter(id__in=action_ids, status=Article.STATUS[1][0]).order_by('-tags__weight').order_by('-views')

    for r_article in related_articles:
        excludes.append(r_article.id)

    _children = []
    if len(related_articles) > 0:
        for r_article in related_articles:
            _child = __get_article_tree(r_article, collection, excludes, level+1)
            _children.append(_child)

    # _child =  { article.title: _children }
    print(article.title)
    _article_seri = Article.ArticleSerializer(article, many=False)
    if len(_children) > 0:
        _child =  { "name": _article_seri.data, "children": _children }
    else:
        _child =  { "name": _article_seri.data }

    return _child




    
