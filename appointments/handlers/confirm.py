from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..forms import ConfirmForm


class ConfirmHandler(AppointmentHandler):
    "Confirm an appointment notificiation."

    keyword = 'confirm'
    help_text = _('To confirm an upcoming appointment send: %(prefix)s %(keyword)s <NAME/ID>')

    def parse_message(self, text):
        "Tokenize message text."
        return {'name': text.strip()}

    def handle(self, text):
        "Match the user to an uncomfirmed notification."
        parsed = self.parse_message(text)
        form = ConfirmForm(data=parsed, connection=self.msg.connection)
        if form.is_valid():
            form.save()
            self.respond(_('Thank you! Your appointment has been confirmed.'))
        else:
            error = form.error()
            if error is None:
                self.unknown()
            else:
                self.respond(error)
        return True
