from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from articles.forms.article import NewArticleForm
from articles.forms.article import UpdateArticleForm
from articles.models.article import Article
from articles.models.content import Content
from articles.models.tag import Tag
from articles.models.content_meta import ContentMeta
from articles.models.content_rating import ContentRating
import pdb;
from django.db import IntegrityError
from django.db.models import F


# Create your views here.

def index(request):
  _top_articles = Article.objects.order_by('-views')[:3]
  _latest_articles = Article.objects.order_by('-created_at')[:4]
  _tags = Tag.objects.order_by('-created_at')[:100]
  _context = {
    'top_articles': _top_articles,
    'latest_articles': _latest_articles,
    'tags': _tags
  }
  return render(request, 'articles/index.html', _context)

def detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    _tags = []
    for tag in article.tags.all():
        _tags.append(tag.slug)

    action_ids = Article.objects.filter(tags__slug__in=_tags).exclude(id=article.id).distinct('id').values_list('id', flat=True)
    related_articles = Article.objects.filter(id__in=action_ids).order_by('-tags__weight').order_by('-views')

    _my_rating = 0
    if request.user is not None:
        try:
            _rating = ContentRating.objects.get(content_id=article.content_set.get(status=1).id, owner_id=request.user.author.id)
            _my_rating = _rating.value
        except ContentRating.DoesNotExist:
            _my_rating = -1
            pass

    _context = {
        'article': article,
        'content': article.active_content,
        'related_articles': related_articles,
        'my_rating': _my_rating
    }
    Article.objects.filter(id=article.id).update(views=F('views') + 1)

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
            flag, message = __save_article(_form.cleaned_data, _user, _metas)
            return HttpResponseRedirect('/')
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
    _uform = UpdateArticleForm(request.POST or None, initial={'article_id': article_id, 'content': _article.active_content().body, 'tags': _article.tags_str()})
    # pdb.set_trace()
    if request.method == 'POST':
        if _uform.is_valid():
            _user = request.user
            _metas = {
                'keys': _uform.data.getlist('meta_keys'),
                'values': _uform.data.getlist('meta_values')
            }
            flag, message = __update_article(_uform.cleaned_data, _user, _article, _metas)
            return HttpResponseRedirect('/')

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

    return flag, message


def __update_article(post, user, article, metas):
    flag = False
    message = []
    try:
        _content = Content(body=post['content'], status=Content._DEFAULT_STATUS, author=user.author)

        article.tags.clear()

        article_tags = []
        _tags = post['tags']
        for _tag in _tags:
            tag, created = Tag.objects.get_or_create(name=_tag.lower(), slug=slugify(_tag))
            if not created:
                tag.increase_weight(1)
            article.tags.add(tag)

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

    return flag, message
