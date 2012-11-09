from __future__ import unicode_literals

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from .base import AppointmentHandler
from ..forms import NewMessageForm
from ..models import Timeline, TimelineSubscription, now


class NewHandler(AppointmentHandler):
    "Subscribes a user to a timeline."

    keyword = 'new'
    help_text = _('To add a user a timeline send: %(prefix)s %(keyword)s <KEY> <NAME/ID> <DATE>. '
        'The date is optional.')

    def parse_message(self, text):
        "Tokenize message text."
        result = {}
        tokens = text.strip().split()
        result['keyword'] = tokens.pop(0)
        if tokens:
            # Next token is the name/id
            result['name'] = tokens.pop(0)
            if tokens:
                # Remaining tokens should be a date string
                result['date'] = ' '.join(tokens)
        return result       

    def handle(self, text):
        "Register user with a given timeline based on the keyword match."
        parsed = self.parse_message(text)
        form = NewMessageForm(data=parsed)
        if form.is_valid():
            result = {}
            timeline = form.cleaned_data['timeline']
            name = form.cleaned_data['name']
            result['timeline'] = timeline
            result['pin'] = name
            result['connection'] = self.msg.connection
            start = form.cleaned_data.get('date', None) or None
            if start is not None:
                result['start'] = start
            else:
                result['start'] = now()
            # Check if already subscribed
            previous = TimelineSubscription.objects.filter(
                Q(Q(end__isnull=True) | Q(end__gte=now())),
                timeline=timeline, connection=self.msg.connection, pin=name
            )
            msg_data = {
                'user': ' %s' % self.msg.contact.name if self.msg.contact else '',
                'date': result['start'].isoformat(),
                'name': name,
                'timeline': timeline.name,
            }
            if previous.exists():
                # Already joined
                response = _('Sorry, you previously registered a %(timeline)s for '
                        '%(name)s. You will be notified when '
                        'it is time for the next appointment.')
                self.respond(response % msg_data)
            else:
                # FIXME: There is a small race condition here that we could
                # create two subscriptions in parallel
                TimelineSubscription.objects.create(**result)
                response = _('Thank you%(user)s! You registered a %(timeline)s for '
                        '%(name)s on %(date)s. You will be notified when '
                        'it is time for the next appointment.')
                self.respond(response % msg_data)
        else:
            # Respond with error message
            if 'keyword' in form.errors:
                # Invalid keyword
                self.respond(_('Sorry, we could not find any appointments for '
                    'the keyword: %(keyword)s') % parsed)
            elif 'name' in form.errors:
                # Name is missing
                self.respond(_('Sorry, you must include a name or id for your '
                    'appointments subscription.'))
            elif 'date'in form.errors:
                # Invalid date format
                self.respond(_('Sorry, we cannot understand that date format. '
                    'For the best results please use the ISO YYYY-MM-DD format.'))
            else:
                # Non-field error
                self.respond(_('Sorry, we cannot understand that message. '
                    'For additional help send: %(prefix)s NEW') % {'prefix': self.prefix})
        return True
