from __future__ import unicode_literals

import datetime

from .base import AppointmentDataTestCase
from ..models import Appointment
from ..tasks import generate_appointments


class AppointmentAppTestCase(AppointmentDataTestCase):
    "Integration test for larger SMS workflow."

    def setUp(self):
        super(AppointmentAppTestCase, self).setUp()
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.connection = self.create_connection()
        self.milestone = self.create_milestone(timeline=self.timeline, offset=1)

    def test_join(self):
        "Join timeline then generate upcoming appointments."
        msg = self.receive('APPT NEW FOO 123', [self.connection])
        reply = self.outbound[0]
        self.assertTrue(reply.text.startswith('Thank you'))
        # Single appointment should be created
        generate_appointments()
        appointment = Appointment.objects.get(milestone=self.milestone)
        tomorrow = datetime.date.today() + datetime.timedelta(days=self.milestone.offset)
        self.assertEqual(tomorrow, appointment.date)