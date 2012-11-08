from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..models import Timeline, TimelineSubscription


class NewHandler(AppointmentHandler):
    "Subscribes a user to a timeline."

    keyword = 'new'

    def help(self):
        "Return help mesage."
        help_text =_('To add a user a timeline send: {0} NEW <NAME/ID> <DATE>. The date is optional.'.format(self.prefix))
        self.respond(help_text)

    def handle(self, text):
        self.respond("Added.")
