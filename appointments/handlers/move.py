from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..forms import MoveForm


class MoveHandler(AppointmentHandler):
    "Reschdule the next appointment for the patient."

    keyword = 'move'
    form = MoveForm
    help_text = _('To reschedule the next appointment send: %(prefix)s %(keyword)s <NAME/ID> <DATE>')
    success_text = _('Thank you! The appointment has been rescheduled.')

    def parse_message(self, text):
        "Tokenize message text."
        result = {}
        tokens = text.strip().split()
        # Next token is the name/id
        result['name'] = tokens.pop(0)
        if tokens:
            # Next token is the status
            result['date'] = tokens.pop(0)
        return result

    def __handle(self, text):
        """
        Reschedule the User's next applicable appointment with the
        supplied date.
        """
        parsed = self.parse_message(text)
        form = MoveForm(data=parsed, connection=self.msg.connection)
        if form.is_valid():
            form.save()
        else:
            # Respond with error message
            if 'name' in form.errors:
                # Name is missing
                self.respond(_('Sorry, you must include a name or id to '
                    'reschedule an appointment.'))
            elif 'date'in form.errors:
                # Invalid date format
                self.respond(_('Sorry, we cannot understand that date format. '
                    'For the best results please use the ISO YYYY-MM-DD format.'))
            else:
                # Non-field error
                self.respond(_('Sorry, we cannot understand that message. '
                    'For additional help send: %(prefix)s MOVE') % {'prefix': self.prefix})
        return True
