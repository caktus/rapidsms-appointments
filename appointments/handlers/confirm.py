from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..forms import ConfirmForm


class ConfirmHandler(AppointmentHandler):
    "Confirm an appointment notificiation."

    keyword = 'confirm'
    form = ConfirmForm
    help_text = _('To confirm an upcoming appointment send: %(prefix)s %(keyword)s <NAME/ID>')
    success_text = _('Thank you! Your appointment has been confirmed.')

    def parse_message(self, text):
        "Tokenize message text."
        return {'name': text.strip()}
