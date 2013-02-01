from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..forms import StatusForm
from ..models import Appointment


class StatusHandler(AppointmentHandler):
    "Set the status of an appointment for the patient."

    keyword = 'status'
    form = StatusForm
    help_text = _('To set the status of the most recent appointment send: %(prefix)s %(keyword)s <NAME/ID> <SAW|MISSED>')
    success_text = _('Thank you! The appointment status has been set.')

    def parse_message(self, text):
        "Tokenize message text."
        result = {}
        tokens = text.strip().split()
        # Next token is the name/id
        result['name'] = tokens.pop(0)
        if tokens:
            # Next token is the status
            result['status'] = tokens.pop(0)
        return result

    def __handle(self, text):
        "Update the User's recent applicable appointment with the supplied status."
        parsed = self.parse_message(text)
        form = StatusForm(data=parsed, connection=self.msg.connection)
        if form.is_valid():
            form.save()
        else:
            # Respond with error message
            if 'name' in form.errors:
                # Name is missing
                self.respond(_('Sorry, you must include a name or id to set '
                    'an appointment status.'))
            else:
                # Non-field error
                self.respond(_('Sorry, we cannot understand that message. '
                    'For additional help send: %(prefix)s NEW') % {'prefix': self.prefix})
        return True
