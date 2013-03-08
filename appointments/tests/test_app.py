from __future__ import unicode_literals

import datetime

from .base import AppointmentDataTestCase
from ..models import Appointment
from ..tasks import generate_appointments, send_appointment_notifications


class AppointmentAppTestCase(AppointmentDataTestCase):
    "Integration test for larger SMS workflow."

    def setUp(self):
        super(AppointmentAppTestCase, self).setUp()
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.milestone = self.create_milestone(timeline=self.timeline, offset=1)
        self.connection = self.lookup_connections('5555555555')[0]

    def test_join(self):
        "Join timeline then generate upcoming appointments."
        msg = self.receive('APPT NEW FOO 123', self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        # Single appointment should be created
        generate_appointments()
        appointment = Appointment.objects.get(connection=self.connection, milestone=self.milestone)
        tomorrow = datetime.date.today() + datetime.timedelta(days=self.milestone.offset)
        self.assertEqual(tomorrow, appointment.date)

    def test_confirm_appointment(self):
        "Generate a notification and confirm an appointment."
        subscription = self.create_timeline_subscription(connection=self.connection, timeline=self.timeline)
        generate_appointments()
        send_appointment_notifications()
        reminder = self.outbound.pop()
        self.assertTrue(reminder.text.startswith('This is a reminder'))
        msg = self.receive('APPT CONFIRM FOO {0}'.format(subscription.pin), self.connection)
        reply = self.outbound.pop()
        self.assertTrue(reply.text.startswith('Thank you'))
        appointment = Appointment.objects.get(connection=self.connection, milestone=self.milestone)
        self.assertTrue(appointment.confirmed)