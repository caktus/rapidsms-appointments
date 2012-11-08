from django.test import TestCase

from ..handlers.new import NewHandler


class NewHandlerTestCase(TestCase):
    "Keyword handler for adding users to timelines"

    def test_help(self):
        "Prefix and keyword should return the help for adding subscriptions."
        replies = NewHandler.test('APPT NEW')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
        self.assertTrue('APPT NEW <KEY> <NAME/ID> <DATE>' in reply)

    def test_match(self):
        "Send a successful match to create user timeline subscription."
        replies = NewHandler.test('APPT NEW foo')
        self.assertEqual(len(replies), 1)
        reply = replies[0]
