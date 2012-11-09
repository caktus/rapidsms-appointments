from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..models import Notification


class ConfirmHandler(AppointmentHandler):
    "Confirm an appointment notificiation."

    keyword = 'confirm'
    help_text = _('To confirm an upcoming appointment send: %(prefix)s %(keyword)s <NAME/ID>')    

    def handle(self, text):
        "Match the user to an uncomfirmed notification."
        return True
