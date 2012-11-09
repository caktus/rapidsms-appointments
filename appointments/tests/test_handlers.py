from __future__ import unicode_literals

from .base import AppointmentDataTestCase
from ..handlers.confirm import ConfirmHandler
from ..handlers.new import NewHandler


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

    def test_help(self):
        "Prefix and keyword should return the help."
        replies = ConfirmHandler.test('APPT CONFIRM')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('APPT CONFIRM <NAME/ID>' in reply)
