# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-05 21:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainserver', '0019_auto_20170328_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='triggered_alarm',
            name='state',
            field=models.CharField(choices=[('AC', 'Active'), ('NS', 'Not Seen'), ('SE', 'Seen'), ('DE', 'Deleted')], max_length=2),
        ),
    ]
