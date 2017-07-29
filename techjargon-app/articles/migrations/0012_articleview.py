# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-21 05:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authors', '0001_initial'),
        ('articles', '0011_auto_20170613_1029'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleView',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.Article')),
                ('author', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='authors.Author')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
