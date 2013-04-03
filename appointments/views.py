from __future__ import unicode_literals

from appointments.unicsv import UnicodeCSVWriter

from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.generic import View
from django.views.generic.base import TemplateView

from django_tables2 import RequestConfig

from .forms import AppointmentFilterForm
from .models import Appointment
from .tables import ApptTable


class AppointmentMixin(object):
    """Allow filtering by"""
    @method_decorator(permission_required('appointments.view_appointment'))
    def dispatch(self, request, *args, **kwargs):
        self.form = AppointmentFilterForm(request.GET)
        if self.form.is_valid():
            self.appointments = self.form.get_appointments()
        else:
            self.appointments = Appointment.objects.none()
        return super(AppointmentMixin, self).dispatch(request, *args, **kwargs)


class AppointmentList(AppointmentMixin, TemplateView):
    """Displays a paginated lits of appointments."""
    template_name = 'appointments/appointment_list.html'
    table_template_name = 'django_tables2/bootstrap-tables.html'
    appts_per_page = 10

    @property
    def page(self):
        return self.request.GET.get('page', 1)

    def get_context_data(self, *args, **kwargs):
        appts_table = ApptTable(self.appointments,
                                template=self.table_template_name)
        appts_table.paginate(page=self.page, per_page=self.appts_per_page)
        RequestConfig(self.request).configure(appts_table)
        return {
            'form': self.form,
            'appts_table': appts_table
        }


class CSVAppointmentList(AppointmentMixin, View):
    """Export filtered reports to a CSV file."""
    # Fields to include in the csv, in order.
    filename = 'appointments'

    def get(self, request, *args, **kwargs):
        if not self.form.is_valid():
            url = reverse('appointment_list')
            if request.GET:
                url = '{0}?{1}'.format(url, request.GET.urlencode())
            return HttpResponseRedirect(url)
        response = HttpResponse(content_type='text/csv')
        content_disposition = 'attachment; filename=%s.csv' % self.filename
        response['Content-Disposition'] = content_disposition
        writer = UnicodeCSVWriter(response)
        writer.writerows(self.get_data())
        return response

    def get_data(self):
        appts_table = ApptTable(self.appointments)
        columns = [x.title() for x in appts_table.columns.names()]
        rows = [columns, ]
        for appointment in appts_table.rows:
            cells = [x for x in appointment]
            row = []
            for cell in cells:
                row.append(cell)
            rows.append(row)
        return rows
