from __future__ import unicode_literals

import datetime

from rapidsms.tests.harness import RapidTest

from .base import AppointmentDataTestCase, Appointment, Milestone, now
from ..tasks import generate_appointments, send_appointment_reminders, APPT_REMINDER


class GenerateAppointmentsTestCase(AppointmentDataTestCase):
    "Task to generate future appointments"

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.offsets = [1, 3, 7, 14, 30]
        for offset in self.offsets:
            self.create_milestone(name='{0} day(s)'.format(offset), offset=offset, timeline=self.timeline)
        self.sub = self.create_timeline_subscription(timeline=self.timeline)
        self.cnx = self.sub.connection

    def test_generate_appointments(self):
        "Test the default task"
        self.assertEqual(0, Appointment.objects.filter(connection=self.cnx).count())
        generate_appointments()
        self.assertEqual(4, Appointment.objects.filter(connection=self.cnx).count())

    def test_generate_appointments_already_exists(self):
        "The task should generate no appointments if the series already exists for the user"
        self.cnx = self.sub.connection
        for offset in self.offsets:
            date = now() + datetime.timedelta(days=offset)
            milestone = Milestone.objects.get(offset=offset)
            self.create_appointment(connection=self.cnx, date=date, milestone=milestone)
        self.assertEqual(5, Appointment.objects.filter(connection=self.cnx).count())
        generate_appointments()
        self.assertEqual(5, Appointment.objects.filter(connection=self.cnx).count())

    def test_generate_appointments_out_of_range(self):
        "The task should generate no appointments if the milestones are out of range"
        Milestone.objects.all().delete()
        offsets = [15, 17]
        for offset in offsets:
            self.create_milestone(name='{0} day(s)'.format(offset), offset=offset, timeline=self.timeline)
        self.assertEqual(0, Appointment.objects.filter(connection=self.cnx).count())
        generate_appointments()
        self.assertEqual(0, Appointment.objects.filter(connection=self.cnx).count())

    def test_generate_appointments_multiple_subscriptions(self):
        "The task should generate appointments for all applicable subscriptions"
        self.assertEqual(0, Appointment.objects.all().count())
        self.create_timeline_subscription(timeline=self.timeline)
        generate_appointments()
        self.assertEqual(8, Appointment.objects.all().count())

    def test_generate_appointments_for_n_days(self):
        "The task should generate appointments when supplied N days as an argument"
        self.assertEqual(0, Appointment.objects.all().count())
        generate_appointments(30)
        self.assertEqual(5, Appointment.objects.all().count())


class SendAppointmentRemindersTestCase(AppointmentDataTestCase, RapidTest):
    "Task to send reminders for upcoming Appointments"

    def setUp(self):
        self.backend = self.create_backend(name='mockbackend')
        self.cnx = self.create_connection(backend=self.backend)
        self.appointment = self.create_appointment(connection=self.cnx)

    def test_send_reminders(self):
        "Test the default task"
        self.assertEqual(0, Appointment.objects.filter(connection=self.cnx, reminded=True).count())
        send_appointment_reminders()
        self.assertEqual(1, Appointment.objects.filter(connection=self.cnx, reminded=True).count())
        msg = APPT_REMINDER % {'date': self.appointment.date}
        self.assertEqual(self.outbound[0].text, msg)
        self.assertEqual(self.outbound[0].connection, self.cnx)

    def test_send_reminders_reminded(self):
        "The task should generate no reminders if a reminder has already been sent"
        self.appointment.reminded = True
        self.appointment.save()
        self.assertEqual(1, Appointment.objects.filter(connection=self.cnx, reminded=True).count())
        send_appointment_reminders()
        self.assertEqual(1, Appointment.objects.filter(connection=self.cnx, reminded=True).count())
        self.assertEqual(0, len(self.outbound))

    def test_send_reminders_out_of_range(self):
        "The task should generate no reminders if the appointment(s) are out of range"
        self.appointment.date = self.appointment.date + datetime.timedelta(days=10)
        self.appointment.save()
        self.assertEqual(1, Appointment.objects.filter(connection=self.cnx, reminded=False).count())
        send_appointment_reminders()
        self.assertEqual(0, Appointment.objects.filter(connection=self.cnx, reminded=True).count())
        self.assertEqual(0, len(self.outbound))

    def test_send_reminders_multiple_users(self):
        "The task should generate reminders for all applicable appointments"
        self.cnx2 = self.create_connection(identity='johndoe', backend=self.backend)
        self.create_appointment(connection=self.cnx2)
        self.assertEqual(0, Appointment.objects.filter(reminded=True).count())
        send_appointment_reminders()
        self.assertEqual(2, Appointment.objects.filter(reminded=True).count())
        self.assertEqual(2, len(self.outbound))

    def test_send_reminders_for_n_days(self):
        "The task should generate appointments when supplied N days as an argument"
        self.create_appointment(connection=self.cnx, date=now() + datetime.timedelta(days=10))
        self.assertEqual(0, Appointment.objects.filter(connection=self.cnx, reminded=True).count())
        send_appointment_reminders(30)
        self.assertEqual(2, Appointment.objects.filter(connection=self.cnx, reminded=True).count())
        self.assertEqual(2, len(self.outbound))
