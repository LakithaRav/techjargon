from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from articles.forms.article import NewArticleForm
from articles.forms.article import UpdateArticleForm
from authors.models.author import Author
from articles.models.article import Article
from articles.models.content import Content
from articles.models.tag import Tag
from articles.models.content_meta import ContentMeta
from articles.models.content_rating import ContentRating
from articles.models.article_view import ArticleView
import pdb;
from django.db import IntegrityError
from django.db.models import F
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import operator
import hashlib


# Create your views here.

def index(request):
  _top_articles = Article.objects.order_by('-views')[:10]
  _latest_articles = Article.objects.order_by('-created_at')[:20]
  _tags = Tag.objects.order_by('-weight')[:50]
  _top_100 = Article.objects.order_by('-views')[:100]

  _tags = sorted(_tags, key=operator.attrgetter('created_at'))

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
    'tags': _tags,
    'meta': _page_meta,
  }
  return render(request, 'articles/index.html', _context)

def search(request):
    # pdb.set_trace()
    _query = request.GET.get('q')
    _page = request.GET.get('page')

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
        'tags': _tags
    }
    return render(request, 'articles/search.html', _context)

def detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    _tags = []
    for tag in article.tags.all():
        _tags.append(tag.slug)

    action_ids = Article.objects.filter(tags__slug__in=_tags).exclude(id=article.id).distinct('id').values_list('id', flat=True)
    related_articles = Article.objects.filter(id__in=action_ids).order_by('-tags__weight').order_by('-views')[:10]

    _total_ratins = ContentRating.objects.filter(content_id__in=article.content_set.values('id')).order_by('owner_id', '-id').distinct('owner_id').count()
    _my_rating = 0
    if hasattr(request.user, 'author'):
        try:
            _rating = ContentRating.objects.get(content_id=article.active_content().id, owner_id=request.user.author.id)
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
        'total_ratins': _total_ratins,
        'full_url_path': request.build_absolute_uri()
    }

    falg, message = __add_view_log(request, article)

    return render(request, 'articles/detail.html', _context)

def history(request, slug, content_id):
    article = get_object_or_404(Article, slug=slug)
    content = Content.objects.get(pk=content_id)
    _context = {
        'article': article,
        'content': content
    }

    return render(request, 'articles/history.html', _context)

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
    flag = False
    message = []
    try:
        # pdb.set_trace()
        nview = None

        # reverse proxy hack
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            request.META['REMOTE_ADDR'] = request.META['HTTP_X_FORWARDED_FOR'].split(",")[0].strip()

        if hasattr(request.user, 'author'):
            nview = ArticleView(ip_address=request.META.get('REMOTE_ADDR'), article=article, author=request.user.author)
        else:
            nview = ArticleView(ip_address=request.META.get('REMOTE_ADDR'), article=article, author=None)

        nview.save()
        Article.objects.filter(id=article.id).update(views=article.articleview_set.count())

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("View log added")
        flag = True

    return flag, message
