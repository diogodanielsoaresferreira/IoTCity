# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-10 17:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SensorData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subscription_id', models.CharField(max_length=50)),
                ('timestamp', models.DateTimeField()),
                ('value', models.IntegerField()),
                ('ttl', models.IntegerField(blank=True, default=120)),
            ],
        ),
    ]
