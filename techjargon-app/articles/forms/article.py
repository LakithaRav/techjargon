from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from articles.models.article import Article


class NewArticleForm(forms.Form):
    title = forms.CharField(max_length=100)
    content = forms.CharField()
    # metas = forms.JSONField() # comes and json object array
    tags = SimpleArrayField(forms.CharField(), delimiter=',')
    meta_keys = SimpleArrayField(forms.CharField(), required=False)
    meta_values = SimpleArrayField(forms.CharField(), required=False)


    class Meta:
        model = Article
        fields = ('title', 'content', 'meta', 'tags', 'meta_keys', 'meta_values')


class UpdateArticleForm(forms.Form):
    article_id = forms.IntegerField()
    # title = forms.CharField(max_length=100)
    content = forms.CharField()
    # metas = forms.JSONField() # comes and json object array
    tags = SimpleArrayField(forms.CharField(), delimiter=',')
    meta_keys = SimpleArrayField(forms.CharField(), required=False)
    meta_values = SimpleArrayField(forms.CharField(), required=False)


    class Meta:
        model = Article
        fields = ('content', 'meta', 'tags', 'meta_keys', 'meta_values')

