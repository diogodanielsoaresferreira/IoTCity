# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-26 21:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainserver', '0016_auto_20170326_1725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='day_week',
            name='day',
            field=models.CharField(choices=[('MO', 'Monday'), ('TU', 'Tuesday'), ('WE', 'Wednesday'), ('TH', 'Thursday'), ('FR', 'Friday'), ('SA', 'Saturday'), ('SU', 'Sunday')], max_length=2),
        ),
    ]