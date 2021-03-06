# Generated by Django 2.2.6 on 2020-02-06 15:27

from django.db import migrations, models


def forwards_func(apps, schema_editor):
    ReceivableType = apps.get_model("leasing", "ReceivableType")
    db_alias = schema_editor.connection.alias

    # Make receivable type "Korko" inactive
    ReceivableType.objects.using(db_alias).filter(id=2).update(is_active=False)


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='receivabletype',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is active?'),
        ),
        migrations.RunPython(forwards_func, migrations.RunPython.noop),
    ]
