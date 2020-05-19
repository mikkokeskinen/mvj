from decimal import Decimal
from itertools import groupby
from operator import itemgetter

from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from rest_framework.response import Response

from leasing.enums import TenantContactType
from leasing.models import Invoice
from leasing.report.excel import ExcelCell, ExcelRow, FormatType, PreviousRowsSumCell, SumCell
from leasing.report.report_base import ReportBase


def get_lease_id(obj):
    return obj.lease.get_identifier_string()


def get_recipient_address(obj):
    return ', '.join(filter(None, [
        obj.recipient.address,
        obj.recipient.postal_code,
        obj.recipient.city
    ]))


class ExtraCityRentReport(ReportBase):
    name = _('Extra city rent')
    description = _('The invoiced rent of the leases that are not in the main city')
    slug = 'extra_city_rent'
    input_fields = {
        'start_date': forms.DateField(label=_('Start date'), required=True),
        'end_date': forms.DateField(label=_('End date'), required=True),
    }
    output_fields = {
        'lease_id': {
            'label': _('Lease id'),
        },
        'tenant_name': {
            'label': _('Tenant name'),
            'width': 50,
        },
        'area_identifier': {
            'label': _('Area identifier'),
            'width': 50,
        },
        'area': {
            'label': _('Area amount'),
        },
        'area_address': {
            'label': _('Address'),
            'width': 50,
        },
        'rent': {
            'label': _('Rent'),
            'format': 'money',
            'width': 13,
        },
    }
    automatic_excel_column_labels = False

    def get_data(self, input_data):
        qs = Invoice.objects.filter(
            (
                Q(rows__billing_period_start_date__gte=input_data['start_date']) &
                Q(rows__billing_period_start_date__lte=input_data['end_date'])
             ) | (
                Q(rows__billing_period_end_date__gte=input_data['start_date']) &
                Q(rows__billing_period_end_date__lte=input_data['end_date'])
            )
        ).exclude(
            lease__municipality=1,  # Helsinki
        ).select_related(
            'lease',
            'lease__identifier',
            'lease__identifier__type',
            'lease__identifier__district',
            'lease__identifier__municipality'
        ).prefetch_related(
            'lease__tenants',
            'lease__tenants__tenantcontact_set',
            'lease__tenants__tenantcontact_set__contact',
            'lease__lease_areas',
            'lease__lease_areas__addresses',
        ).order_by(
            'lease__identifier__municipality__identifier',
            'lease__identifier__type__identifier',
            'lease__identifier__district__identifier',
            'lease__identifier__sequence',
        )

        aggregated_data = []

        for lease, invoices in groupby(qs, lambda x: x.lease):
            total_rent = Decimal(0)
            contacts = set()
            for invoice in invoices:
                total_rent += invoice.total_amount

            # Do this in code so that the prefetch is used
            for tenant in lease.tenants.all():
                for tc in tenant.tenantcontact_set.all():
                    if tc.type != TenantContactType.TENANT:
                        continue

                    if (tc.end_date is None or tc.end_date >= input_data['start_date']) and \
                            (tc.start_date is None or tc.start_date <= input_data['end_date']):
                        contacts.add(tc.contact)

            addresses = []
            for lease_area in lease.lease_areas.all():
                if lease_area.archived_at:
                    continue

                addresses.extend([la.address for la in lease_area.addresses.all()])

            aggregated_data.append(
                {
                    'municipality_name': lease.identifier.municipality.name,
                    'lease_id': lease.get_identifier_string(),
                    'tenant_name': ', '.join([c.get_name() for c in contacts]),
                    'area_identifier': ', '.join(
                        [la.identifier for la in lease.lease_areas.all() if la.archived_at is None]),
                    'area': sum([la.area for la in lease.lease_areas.all() if la.archived_at is None]),
                    'area_address': ' / '.join(addresses),
                    'rent': total_rent,
                }
            )

        return aggregated_data

    def get_response(self, request):
        report_data = self.get_data(self.get_input_data(request))

        if request.accepted_renderer.format != 'xlsx':
            serialized_report_data = self.serialize_data(report_data)

            return Response(serialized_report_data)

        grouped_data = groupby(report_data, itemgetter('municipality_name'))

        result = []
        totals_row_nums = []
        data_row_num = 0

        for municipality_name, data in grouped_data:
            result.append(ExcelRow())
            data_row_num += 1
            result.append(ExcelRow())
            data_row_num += 1

            result.append(ExcelRow([ExcelCell(column=0, value=municipality_name, format_type=FormatType.BOLD)]))
            data_row_num += 1

            result.append(ExcelRow())
            data_row_num += 1

            column_names_row = ExcelRow()
            for index, field_name in enumerate(self.output_fields.keys()):
                field_label = self.get_output_field_attr(field_name, 'label', default=field_name)
                column_names_row.cells.append(ExcelCell(column=index, value=str(field_label),
                                                        format_type=FormatType.BOLD))
            result.append(column_names_row)
            data_row_num += 1

            row_count = 0
            for datum in data:
                datum.pop('municipality_name')
                result.append(datum)
                row_count += 1
                data_row_num += 1

            total_row = ExcelRow([
                ExcelCell(column=0, value='{} {}'.format(municipality_name, _('Total')),
                          format_type=FormatType.BOLD),
                PreviousRowsSumCell(column=3, count=row_count),
                PreviousRowsSumCell(column=5, count=row_count, format_type=FormatType.BOLD_MONEY),
            ])
            result.append(total_row)
            totals_row_nums.append(data_row_num)

            data_row_num += 1

        result.append(ExcelRow())

        totals_row = ExcelRow()
        totals_row.cells.append(ExcelCell(column=0, value=str(_('Grand total')), format_type=FormatType.BOLD))

        total_area_sum_cell = SumCell(column=3)
        total_rent_sum_cell = SumCell(column=5, format_type=FormatType.BOLD_MONEY)
        for totals_row_num in totals_row_nums:
            total_area_sum_cell.add_target_range((totals_row_num, 3, totals_row_num, 3))
            total_rent_sum_cell.add_target_range((totals_row_num, 5, totals_row_num, 5))

        totals_row.cells.append(total_area_sum_cell)
        totals_row.cells.append(total_rent_sum_cell)
        result.append(totals_row)

        return Response(result)