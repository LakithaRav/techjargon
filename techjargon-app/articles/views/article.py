from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.db import IntegrityError
from django.db.models import F
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import operator
import hashlib
import pdb
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
  _top_articles = Article.objects.order_by('-views')[:10]
  _latest_articles = Article.objects.order_by('-created_at')[:20]
  _tags = Tag.objects.order_by('-weight')[:50]
  _top_100 = Article.objects.order_by('-views')[:100]

  _tags = sorted(_tags, key=operator.attrgetter('created_at'))
  _sugg_articles = []
  if request.user.is_authenticated:
      _sugg_tags = get_suggetion_tags(request.user.id)
      _sugg_articles = Article.objects.filter(tags__pk__in=_sugg_tags).distinct('id').order_by('-id', '-created_at')[:10]
      _sugg_articles = sorted(_sugg_articles, key=operator.attrgetter('views', 'rating'), reverse=True)

  _page_meta = {
    'keywords': '',
    'article_titles': '',
    'full_url_path': request.build_absolute_uri(),
  }

  for article in _top_articles:
      _page_meta['keywords'] += article.title + ','

  for article in _latest_articles:
      _page_meta['keywords'] += article.title + ','

  for article in _top_100:
      _page_meta['article_titles'] += article.title.title() + ','

  _context = {
    'top_articles': _top_articles,
    'latest_articles': _latest_articles,
    'suggested_articles': _sugg_articles,
    'tags': _tags,
    'meta': _page_meta,
  }
  return render(request, 'articles/index.html', _context)

def search(request):
    # pdb.set_trace()
    _query = request.GET.get('q')
    _page = request.GET.get('page')
    # _page = int(_page)

    _articles = Article.objects.annotate(search=SearchVector('title', 'tags__name'),).filter(search=_query).distinct('id')
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
        _tags.append(tag.slug)

    action_ids = Article.objects.filter(tags__slug__in=_tags).exclude(id=article.id).distinct('id').values_list('id', flat=True)
    related_articles = Article.objects.filter(id__in=action_ids).order_by('-tags__weight').order_by('-views')[:10]

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
        pdb.set_trace()
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


def get_suggetion_tags(user_id):
    primary_tags = []
    optional_tags = []

    _article_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[0][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')
    _tags_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[1][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')
    _rating_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[2][0], preferece=UserTag.PREFERENCE_TYPE[0][0]).order_by('-created_at')

    optional_tags += _article_tags
    optional_tags += _tags_tags
    optional_tags += _rating_tags

    _article_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[0][0], preferece=UserTag.PREFERENCE_TYPE[1][0]).order_by('-created_at')
    _tags_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[1][0], preferece=UserTag.PREFERENCE_TYPE[1][0]).order_by('-created_at')
    _rating_tags = UserTag.objects.filter(user_id=user_id, source=UserTag.SOURCE_TYPE[2][0], preferece=UserTag.PREFERENCE_TYPE[1][0]).order_by('-created_at')

    primary_tags += _article_tags
    primary_tags += _tags_tags
    primary_tags += _rating_tags

    tags = []
    for tag in optional_tags:
        tags.append(tag.tag_id)

    return tags
