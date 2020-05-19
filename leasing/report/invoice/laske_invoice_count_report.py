import datetime
from collections import Counter

from dateutil.relativedelta import relativedelta
from django import forms
from django.db.models.aggregates import Count
from django.db.models.functions.datetime import TruncDate
from django.utils.timezone import make_aware
from django.utils.translation import ugettext_lazy as _

from leasing.models import Invoice, Rent
from leasing.report.report_base import ReportBase


class LaskeInvoiceCountReport(ReportBase):
    name = _('Count of Invoices sent to Laske per day')
    description = _('Shows actual sent invoice counts until yesterday, and estimated counts for today and beyond')
    slug = 'laske_invoice_count'
    input_fields = {
        'start_date': forms.DateField(label=_('Start date'), required=True),
        'end_date': forms.DateField(label=_('End date'), required=True),
    }
    output_fields = {
        'send_date': {
            'label': _('Send date'),
            'format': 'date',
        },
        'invoice_count': {
            'label': _('Invoice count'),
        },
        'is_estimate': {
            'label': _('Is estimate?'),
            'format': 'boolean',
        },
    }

    def get_data(self, input_data):
        today = datetime.date.today()
        query_start_date = min(input_data['start_date'], input_data['end_date'])
        query_end_date = max(input_data['end_date'], input_data['start_date'])
        estimate_start_date = None
        estimate_end_date = None

        data = Counter()
        tmp_date = query_start_date
        while tmp_date < query_end_date:
            data[tmp_date] = 0
            tmp_date += datetime.timedelta(days=1)

        if query_start_date >= today:
            estimate_start_date = query_start_date
            query_start_date = None
            estimate_end_date = query_end_date
            query_end_date = None
        else:
            if query_end_date >= today:
                estimate_start_date = today
                estimate_end_date = query_end_date
                query_end_date = today - datetime.timedelta(days=1)

        if query_start_date and query_end_date:
            for result in Invoice.objects.annotate(send_date=TruncDate('sent_to_sap_at')).filter(
                sent_to_sap_at__gte=make_aware(datetime.datetime.combine(query_start_date, datetime.time(0, 0))),
                sent_to_sap_at__lte=make_aware(datetime.datetime.combine(query_end_date, datetime.time(23, 59))),
            ).values('send_date').annotate(invoice_count=Count('id')).order_by('send_date'):
                data[result['send_date']] = result['invoice_count']

        if estimate_start_date and estimate_end_date:
            due_dates_start = estimate_start_date + relativedelta(months=1)
            due_dates_end = estimate_end_date + relativedelta(months=1)

            rents = Rent.objects.filter(
                lease__end_date__gte=today,
                lease__is_invoicing_enabled=True
            ).select_related('lease', 'lease__type')[:5000]

            for rent in rents:
                due_dates = rent.get_due_dates_for_period(due_dates_start, due_dates_end)

                for due_date in due_dates:
                    data[due_date - relativedelta(months=1)] += 1

        return [{'send_date': i[0], 'invoice_count': i[1], 'is_estimate': i[0] >= today} for i in data.items()]