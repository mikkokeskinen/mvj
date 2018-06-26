# Generated by Django 2.0.6 on 2018-06-25 11:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0016_make_invoice_billing_period_nullable'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvoicePayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('deleted', models.DateTimeField(editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Time created')),
                ('modified_at', models.DateTimeField(auto_now=True, verbose_name='Time modified')),
                ('paid_amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Paid amount')),
                ('paid_date', models.DateField(verbose_name='Paid date')),
            ],
            options={
                'verbose_name': 'Invoice payment',
                'verbose_name_plural': 'Invoice payments',
            },
        ),
        migrations.CreateModel(
            name='InvoiceSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_period_start_date', models.DateField(blank=True, null=True, verbose_name='Billing period start date')),
                ('billing_period_end_date', models.DateField(blank=True, null=True, verbose_name='Billing period end date')),
                ('lease', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='invoicesets', to='leasing.Lease', verbose_name='Lease')),
            ],
            options={
                'verbose_name': 'Invoice set',
                'verbose_name_plural': 'Invoice set',
            },
        ),
        migrations.AlterModelOptions(
            name='invoicerow',
            options={'base_manager_name': 'objects', 'verbose_name': 'Invoice row', 'verbose_name_plural': 'Invoice rows'},
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='paid_amount',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='paid_date',
        ),
        migrations.AddField(
            model_name='invoice',
            name='credited_invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='credited_invoices', to='leasing.Invoice', verbose_name='Credited invoice'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='number',
            field=models.PositiveIntegerField(blank=True, null=True, unique=True, verbose_name='Number'),
        ),
        migrations.AddField(
            model_name='invoicepayment',
            name='invoice',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='leasing.Invoice', verbose_name='Invoice'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='invoiceset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='invoices', to='leasing.InvoiceSet', verbose_name='Invoice set'),
        ),
    ]
