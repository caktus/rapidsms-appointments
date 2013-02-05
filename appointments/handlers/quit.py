from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..forms import QuitForm


class QuitHandler(AppointmentHandler):
    "Unsubscribes a user to a timeline."

    keyword = 'quit'
    form = QuitForm
    success_text = _('Thank you%(user)s! You unsubcribed from the %(timeline)s for '
        '%(name)s on %(date)s. You will be no longer be notified when it is time for the next appointment.')
    help_text = _('To unsubcribe a user from a timeline send: %(prefix)s %(keyword)s <KEY> <NAME/ID> <DATE>. '
        'The date is optional.')

    def parse_message(self, text):
        "Tokenize message text."
        result = {}
        tokens = text.strip().split()
        result['keyword'] = tokens.pop(0)
        if tokens:
            # Next token is the name/id
            result['name'] = tokens.pop(0)
            if tokens:
                # Remaining tokens should be a date string
                result['date'] = ' '.join(tokens)
        return result

    def __handle(self, text):
        "Unsubscribe user with a given timeline based on the keyword match."
        parsed = self.parse_message(text)
        form = QuitForm(data=parsed, connection=self.msg.connection)
        if form.is_valid():
            result = {}
        else:
            # Respond with error message
            if 'keyword' in form.errors:
                # Invalid keyword
                self.respond(_('Sorry, we could not find any appointments for '
                    'the keyword: %(keyword)s') % parsed)
            elif 'name' in form.errors:
                # Name is missing
                self.respond(_('Sorry, you must include a name or id for your '
                    'appointments subscription.'))
            elif 'date'in form.errors:
                # Invalid date format
                self.respond(_('Sorry, we cannot understand that date format. '
                    'For the best results please use the ISO YYYY-MM-DD format.'))
            else:
                # Non-field error
                self.respond(_('Sorry, we cannot understand that message. '
                    'For additional help send: %(prefix)s QUIT') % {'prefix': self.prefix})
        return True
