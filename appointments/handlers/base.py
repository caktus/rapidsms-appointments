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
