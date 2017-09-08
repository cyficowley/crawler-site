# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-11 19:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='redirects',
            options={'verbose_name_plural': 'redirects'},
        ),
        migrations.AlterModelOptions(
            name='sites',
            options={'verbose_name_plural': 'sites'},
        ),
        migrations.AlterModelOptions(
            name='statuses',
            options={'verbose_name_plural': 'statuses'},
        ),
        migrations.AlterField(
            model_name='redirects',
            name='new_url',
            field=models.CharField(max_length=1000, verbose_name='to'),
        ),
        migrations.AlterField(
            model_name='redirects',
            name='old_url',
            field=models.CharField(max_length=1000, verbose_name='from'),
        ),
        migrations.AlterField(
            model_name='sites',
            name='list',
            field=models.CharField(max_length=1000, verbose_name='linked from'),
        ),
        migrations.AlterField(
            model_name='statuses',
            name='code',
            field=models.CharField(max_length=1000, verbose_name='status code'),
        ),
    ]
