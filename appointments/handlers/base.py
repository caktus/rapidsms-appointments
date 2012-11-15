from __future__ import unicode_literals

import re

from rapidsms.contrib.handlers.handlers.keyword import KeywordHandler


class AppointmentHandler(KeywordHandler):
    "Base keyword handler for the APPT prefix."

    prefix = 'APPT'

    @classmethod
    def _keyword(cls):
        if hasattr(cls, "keyword"):
            pattern = r"^\s*(?:%s)\s*(?:%s)(?:[\s,;:]+(.+))?$" % (cls.prefix, cls.keyword)
            return re.compile(pattern, re.IGNORECASE)

    def help(self):
        "Return help mesage."
        if self.help_text:
            keyword = self.keyword.split('|')[0].upper()
            help_text = self.help_text % {'prefix': self.prefix, 'keyword': keyword}
        self.respond(help_text)

    def unknown(self):
        "Common fallback for unknown errors."
        keyword = self.keyword.split('|')[0].upper()
        params = {'prefix': self.prefix, 'keyword': keyword}
        self.respond(_('Sorry, we cannot understand that message. '
            'For additional help send: %(prefix)s %(keyword)s') % params)
