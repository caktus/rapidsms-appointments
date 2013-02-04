from __future__ import unicode_literals

from datetime import timedelta

from .base import (AppointmentDataTestCase, Notification, Appointment,
    TimelineSubscription, now)
from ..handlers.confirm import ConfirmHandler
from ..handlers.new import NewHandler
from ..handlers.quit import QuitHandler


class NewHandlerTestCase(AppointmentDataTestCase):
    "Keyword handler for adding users to timelines"

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')

    def test_help(self):
        "Prefix and keyword should return the help for adding subscriptions."
        replies = NewHandler.test('APPT NEW')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('APPT NEW <KEY> <NAME/ID> <DATE>' in reply)

    def test_match(self):
        "Send a successful match to create user timeline subscription."
        replies = NewHandler.test('APPT NEW foo bar')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_match_with_date(self):
        "Use start date if given."
        replies = NewHandler.test('APPT NEW foo bar 2012-01-01')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_no_keyword_match(self):
        "Keyword does not match any existing timelines."
        self.timeline.delete()
        replies = NewHandler.test('APPT NEW foo bar')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_no_name_given(self):
        "No name is given."
        replies = NewHandler.test('APPT NEW foo')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_invalid_date_format_given(self):
        "Invalid date format."
        replies = NewHandler.test('APPT NEW foo bar baz')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_already_joined(self):
        "Attempting to register and already registered connection/name pair."
        connection = self.create_connection()
        NewHandler._mock_backend = connection.backend
        self.create_timeline_subscription(timeline=self.timeline,
            connection=connection, pin='bar')
        replies = NewHandler.test('APPT NEW foo bar', identity=connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))
        del NewHandler._mock_backend


class ConfirmHandlerTestCase(AppointmentDataTestCase):
    "Keyword handler for confirming appointments."

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.connection = self.create_connection()
        self.subscription = self.create_timeline_subscription(
            timeline=self.timeline, connection=self.connection, pin='bar')
        ConfirmHandler._mock_backend = self.connection.backend
        self.milestone = self.create_milestone(timeline=self.timeline)
        self.appointment = self.create_appointment(milestone=self.milestone)
        self.notification = self.create_notification(appointment=self.appointment)

    def test_help(self):
        "Prefix and keyword should return the help."
        replies = ConfirmHandler.test('APPT CONFIRM')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('APPT CONFIRM <NAME/ID>' in reply)

    def test_appointment_confirmed(self):
        "Successfully confirm an upcoming appointment."
        replies = ConfirmHandler.test('APPT CONFIRM bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'))
        notification = Notification.objects.get(pk=self.notification.pk)
        self.assertTrue(notification.confirmed)
        self.assertEqual(notification.status, Notification.STATUS_CONFIRMED)
        appointment = Appointment.objects.get(pk=self.appointment.pk)
        self.assertTrue(appointment.confirmed)

    def test_no_upcoming_appointment(self):
        "Matched user has no upcoming appointment notifications."
        self.notification.delete()
        replies = ConfirmHandler.test('APPT CONFIRM bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no unconfirmed' in reply)

    def test_already_confirmed(self):
        "Matched user has already confirmed the upcoming appointment."
        self.notification.confirm()
        replies = ConfirmHandler.test('APPT CONFIRM bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('no unconfirmed' in reply)

    def test_no_subscription(self):
        "Name/ID does not match a subscription."
        self.subscription.delete()
        replies = ConfirmHandler.test('APPT CONFIRM bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('does not match an active subscription' in reply)

    def test_subscription_ended(self):
        "Name/ID subscription has ended."
        self.subscription.end = now()
        self.subscription.save()
        replies = ConfirmHandler.test('APPT CONFIRM bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('does not match an active subscription' in reply)


class QuitHandlerTestCase(AppointmentDataTestCase):
    "Keyword handler for unsubscribing users to timelines"

    def setUp(self):
        self.timeline = self.create_timeline(name='Test', slug='foo')
        self.connection = self.create_connection()
        self.subscription = self.create_timeline_subscription(
            timeline=self.timeline, connection=self.connection, pin='bar')
        QuitHandler._mock_backend = self.connection.backend

    def test_help(self):
        "Prefix and keyword should return the help for quitting a subscription."
        replies = QuitHandler.test('APPT QUIT', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('APPT QUIT <KEY> <NAME/ID> <DATE>' in reply)

    def test_match(self):
        "Send a successful match to end a timeline subscription."
        replies = QuitHandler.test('APPT QUIT foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)

    def test_match_with_date(self):
        "Use end date if given."
        end = (now() + timedelta(hours=1)).strftime('%Y-%m-%d')
        replies = QuitHandler.test('APPT QUIT foo bar %s' % end,
                                    identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Thank you'), reply)
        self.assertEqual(end, TimelineSubscription.objects.all()[0].end.strftime('%Y-%m-%d'))

    def test_past_end_date(self):
        "Use end date that is in the past."
        yesterday = (now() - timedelta(days=1)).strftime('%Y-%m-%d')
        replies = QuitHandler.test('APPT QUIT foo bar %s' % yesterday,
                                    identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('must be in the future' in reply)

    def test_no_keyword_match(self):
        "Keyword does not match any existing timelines."
        self.timeline.delete()
        replies = QuitHandler.test('APPT QUIT foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_no_name_given(self):
        "No name is given."
        replies = QuitHandler.test('APPT QUIT foo', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_invalid_date_format_given(self):
        "Invalid date format."
        replies = QuitHandler.test('APPT QUIT foo bar baz', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))

    def test_already_quit(self):
        "Attempting to unsubscribe and already unsubcribed connection/name pair."
        self.subscription.end = now()
        self.subscription.save()
        replies = QuitHandler.test('APPT QUIT foo bar', identity=self.connection.identity)
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue(reply.startswith('Sorry'))
