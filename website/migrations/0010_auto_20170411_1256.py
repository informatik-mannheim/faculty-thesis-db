# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-11 10:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_auto_20170411_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thesis',
            name='assessor',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='website.Assessor'),
        ),
    ]