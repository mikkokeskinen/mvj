# Generated by Django 2.2.6 on 2020-02-13 13:58

from django.db import migrations, models
import django.db.models.deletion
import enumfields.fields
import leasing.enums


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0002_add_is_active_to_receivable_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='leasebasisofrent',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='leasing.LeaseBasisOfRent', verbose_name='Lease basis of rent'),
        ),
        migrations.AddField(
            model_name='leasebasisofrent',
            name='type',
            field=enumfields.fields.EnumField(default='lease', enum=leasing.enums.BasisOfRentType, max_length=20, verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='leasebasisofrent',
            name='zone',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Zone'),
        ),
    ]
