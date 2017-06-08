from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from .forms.article import NewArticleForm
from .forms.article import UpdateArticleForm
from .models.article import Article
from .models.content import Content
from .models.tag import Tag
from .models.content_meta import ContentMeta
import pdb;
from django.db import IntegrityError
from django.db.models import F


# Create your views here.

def index(request):
  _top_articles = Article.objects.order_by('-views')[:3]
  _latest_articles = Article.objects.order_by('-created_at')[:4]
  _context = {
    'top_articles': _top_articles,
    'latest_articles': _latest_articles,
  }
  return render(request, 'articles/index.html', _context)

def detail(request, slug):
    article = get_object_or_404(Article, slug=slug)
    _context = {
        'article': article,
        'content': article.active_content
    }
    article.views = F('views') +1
    article.save()
    
    return render(request, 'articles/detail.html', _context)

def history(request, slug, content_id):
    article = get_object_or_404(Article, slug=slug)
    content = Content.objects.get(pk=content_id)
    _context = {
        'article': article,
        'content': content
    }
    article.views = F('views') +1
    article.save()
    
    return render(request, 'articles/history.html', _context)

@login_required
def add(request):
    if request.method == 'POST':
        # pdb.set_trace()
        _form = NewArticleForm(request.POST)
        if _form.is_valid():
            _user = request.user
            flag, message = __save_article(_form.cleaned_data, _user)
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
            flag, message = __update_article(_uform.cleaned_data, _user, _article)
            return HttpResponseRedirect('/')

    _context = {
        'article': _article,
        'uform': _uform
    }
    return render(request, 'articles/update.html', _context)


# private

def __save_article(post, user):
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
            tag, created = Tag.objects.get_or_create(name=_tag)
            _article.tags.add(tag)

        # pdb.set_trace()
        # _article.content_set.update(status=Content.STATUS[0][0])
        _content.article = _article
        _content.save()

        _meta_keys = post['meta_keys']
        _meta_values = post['meta_values']

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("Article created successfully")
        flag = True

    return flag, message


def __update_article(post, user, article):
    flag = False
    message = []
    try:
        _content = Content(body=post['content'], status=Content._DEFAULT_STATUS, author=user.author)

        article.tags.all().delete()

        article_tags = []
        _tags = post['tags']
        for _tag in _tags:
            tag, created = Tag.objects.get_or_create(name=_tag)
            article.tags.add(tag)

        article.content_set.update(status=Content.STATUS[0][0])
        _content.article = article
        _content.save()

        # _meta_keys = post['meta_keys']
        # _meta_values = post['meta_values']

    except IntegrityError as e:
        message.append(e)
        pass
    else:
        message.append("Content updated successfully")
        flag = True

    return flag, message


