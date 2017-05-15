# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-12 11:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0006_auto_20170510_1447'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='tenant',
        ),
        migrations.AddField(
            model_name='invoice',
            name='tenants',
            field=models.ManyToManyField(to='leasing.Tenant'),
        ),
    ]
