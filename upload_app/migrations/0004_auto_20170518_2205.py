# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-18 14:05
from __future__ import unicode_literals

from django.db import migrations, models
import upload_app.models


class Migration(migrations.Migration):

    dependencies = [
        ('upload_app', '0003_auto_20170515_2350'),
    ]

    operations = [
        migrations.CreateModel(
            name='Document_face',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(blank=True, max_length=255)),
                ('document', models.FileField(upload_to=upload_app.models.user_directory_path)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AlterField(
            model_name='document',
            name='document',
            field=models.FileField(upload_to=upload_app.models.user_directory_path),
        ),
    ]
