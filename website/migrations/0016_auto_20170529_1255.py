# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-29 10:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0015_thesis_excom_reject_reason'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExcomChairman',
            fields=[
                ('first_name', models.CharField(max_length=30, verbose_name='Vorname')),
                ('last_name', models.CharField(max_length=30, verbose_name='Nachname')),
                ('initials', models.CharField(max_length=10, verbose_name='Kürzel')),
                ('id', models.CharField(max_length=30, primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='thesis',
            name='excom_approval_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='thesis',
            name='excom_chairman',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='website.ExcomChairman'),
        ),
    ]
