# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-11-01 08:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ux', '0003_auto_20161027_0825'),
    ]

    operations = [
        migrations.CreateModel(
            name='BiPnic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device', models.CharField(blank=True, max_length=100, null=True)),
                ('vswitch', models.ManyToManyField(to='ux.BiVswitch')),
            ],
        ),
        migrations.CreateModel(
            name='BiPortgroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('vlanId', models.CharField(blank=True, max_length=100, null=True)),
                ('vswitch', models.ManyToManyField(to='ux.BiVswitch')),
            ],
        ),
    ]
