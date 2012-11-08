from __future__ import unicode_literals

from .base import AppointmentHandler
from ..models import Timeline, TimelineSubscription


class NewHandler(AppointmentHandler):
    "Subscribes a user to a timeline."

    keyword = 'new'

    def handle(self, text):
        self.respond("Added.")
