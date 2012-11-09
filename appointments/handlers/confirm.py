from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..models import Notification


class ConfirmHandler(AppointmentHandler):
    "Confirm an appointment notificiation."

    keyword = 'confirm'

    def help(self):
        "Return help mesage."
        keyword = self.keyword.split('|')[0].upper()
        help_text = _('To confirm an upcoming appointment send: %(prefix)s %(keyword)s <NAME/ID>')
        self.respond(help_text % {'prefix': self.prefix, 'keyword': keyword})     

    def handle(self, text):
        "Match the user to an uncomfirmed notification."
        return True
