# Generated by Django 2.1.7 on 2019-03-01 12:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0053_decisiontype_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='collectioncourtdecision',
            name='decision_date',
            field=models.DateField(blank=True, null=True, verbose_name='Decision date'),
        ),
        migrations.AddField(
            model_name='collectioncourtdecision',
            name='note',
            field=models.TextField(blank=True, null=True, verbose_name='Note'),
        ),
    ]