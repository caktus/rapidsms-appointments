from __future__ import unicode_literals

from django import forms
from django.db.models import Q
from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from .models import Timeline, TimelineSubscription, Appointment, Notification, now


class PlainErrorList(ErrorList):
    "Customization of the error list for including in an SMS message."

    def as_text(self):
        if not self: return ''
        return ''.join(['%s' % force_unicode(e) for e in self])


class HandlerForm(forms.Form):
    "Base form class for validating SMS handler message data."

    def __init__(self, *args, **kwargs):
        self.connection = kwargs.pop('connection', None)
        kwargs['error_class'] = PlainErrorList
        super(HandlerForm, self).__init__(*args, **kwargs)

    def error(self):
        "Condense form errors to single error message."
        errors = self.errors
        error = None
        if self.errors:
            # Return first field error based on field order
            for field in self.fields:
                if field in errors:
                    error = errors[field].as_text()
                    break
            if error is None and NON_FIELD_ERRORS in errors:
                error = self.errors[NON_FIELD_ERRORS].as_text()
        return error

    def save(self):
        "Update necessary data and return parameters for the success message."
        return {}


class NewForm(HandlerForm):
    "Register user for new timeline."

    keyword = forms.CharField()
    name = forms.CharField(error_messages={
        'required': _('Sorry, you must include a name or id for your '
            'appointments subscription.')
    })
    date = forms.DateTimeField(required=False, error_messages={
        'invalid': _('Sorry, we cannot understand that date format. '
            'For the best results please use the ISO YYYY-MM-DD format.')
    })

    def clean_date(self):
        "Date must be today or in the future"
        date = self.cleaned_date.get('date', None)
        if date and date < now():
            raise forms.ValidationError(_('Sorry, the supplied date %s must '
                'be in the future: %s') % date)

    def clean_keyword(self):
        "Check if this keyword is associated with any timeline."
        keyword = self.cleaned_data.get('keyword', '')
        match = None
        if keyword:
            # Query DB for valid keywords
            for timeline in Timeline.objects.filter(slug__icontains=keyword):
                if keyword.strip().lower() in timeline.keywords:
                    match = timeline
                    break
        if match is None:
            # Invalid keyword
            raise forms.ValidationError(_('Sorry, we could not find any appointments for '
                    'the keyword: %s') % keyword)
        else:
            self.cleaned_data['timeline'] = match
        return keyword

    def clean(self):
        "Check for previous subscription."
        timeline = self.cleaned_data.get('timeline', None)
        name = self.cleaned_data.get('name', None)
        if name is not None and timeline is not None:
            previous = TimelineSubscription.objects.filter(
                Q(Q(end__isnull=True) | Q(end__gte=now())),
                timeline=timeline, connection=self.connection, pin=name
            )
            if previous.exists():
                params = {'timeline': timeline.name, 'name': name}
                message = _('Sorry, you previously registered a %(timeline)s for '
                        '%(name)s. You will be notified when '
                        'it is time for the next appointment.') % params
                raise forms.ValidationError(message)
        return self.cleaned_data

    def save(self):
        if not self.is_valid():
            return None
        timeline = self.cleaned_data['timeline']
        name = self.cleaned_data['name']
        start = self.cleaned_data.get('date', now()) or now()
        # FIXME: There is a small race condition here that we could
        # create two subscriptions in parallel
        TimelineSubscription.objects.create(
            timeline=timeline, start=start, pin=name,
            connection=self.connection
        )
        user = ' %s' % self.connection.contact.name if self.connection.contact else ''
        return {
            'user': user,
            'date': start,
            'name': name,
            'timeline': timeline.name,
        }


class ConfirmForm(HandlerForm):
    "Confirm an upcoming appointment."

    name = forms.CharField()

    def clean_name(self):
        "Find last unconfirmed notification for upcoming appointment."
        name = self.cleaned_data.get('name', '')
        # name should be a pin for an active timeline subscription
        timelines = TimelineSubscription.objects.filter(
            Q(Q(end__gte=now()) | Q(end__isnull=True)),
            connection=self.connection, pin=name
        ).values_list('timeline', flat=True)
        if not timelines:
            # PIN doesn't match an active subscription for this connection
            raise forms.ValidationError(_('Sorry, name/id does not match an active subscription.'))
        try:
            notification = Notification.objects.filter(
                status=Notification.STATUS_SENT,
                confirmed__isnull=True,
                appointment__confirmed__isnull=True,
                appointment__reschedule__isnull=True,
                appointment__date__lte=now(),
                appointment__milestone__timeline__in=timelines
            ).order_by('-sent')[0]
        except IndexError:
            # No unconfirmed notifications
            raise forms.ValidationError(_('Sorry, you have no unconfirmed appointment notifications.'))
        else:
            self.cleaned_data['notification'] = notification
        return name

    def save(self):
        "Mark the current notification as confirmed and return it."
        if not self.is_valid():
            return None
        notification = self.cleaned_data['notification']
        notification.confirm()
        return {}


class QuitForm(HandlerForm):
    "Unsubscribes a user from a timeline by populating the end date."

    keyword = forms.CharField()
    name = forms.CharField(error_messages={
        'required': _('Sorry, you must include a name or id for your '
            'unsubscription.')
    })
    date = forms.DateTimeField(required=False, error_messages={
        'invalid': _('Sorry, we cannot understand that date format. '
            'For the best results please use the ISO YYYY-MM-DD format.')
    })

    def clean_keyword(self):
        "Check if this keyword is associated with any timeline."
        keyword = self.cleaned_data.get('keyword', '')
        match = None
        if keyword:
            # Query DB for valid keywords
            for timeline in Timeline.objects.filter(slug__icontains=keyword):
                if keyword.strip().lower() in timeline.keywords:
                    match = timeline
                    break
        if match is None:
            # Invalid keyword
            raise forms.ValidationError(_('Sorry, we could not find any appointments for '
                    'the keyword: %s') % keyword)
        else:
            self.cleaned_data['timeline'] = match
        return keyword

    def clean_date(self):
        "Ensure the date to reschedule is in the future"
        date = self.cleaned_data.get('date')
        # date should be in the future
        if date and date.date() < now().date():
            raise forms.ValidationError(_('Sorry, the reschedule date must be in the future.'))
        return date

    def clean(self):
        "Check for previous subscription."
        timeline = self.cleaned_data.get('timeline', None)
        name = self.cleaned_data.get('name', None)
        if name is not None and timeline is not None:
            previous = TimelineSubscription.objects.filter(
                Q(Q(end__isnull=True) | Q(end__gte=now())),
                timeline=timeline, connection=self.connection, pin=name
            )
            if not previous.exists():
                params = {'timeline': timeline.name, 'name': name}
                message = _('Sorry, you have not registered a %(timeline)s for '
                        '%(name)s.') % params
                raise forms.ValidationError(message)
            self.cleaned_data['subscription'] = previous[0]
        return self.cleaned_data

    def save(self):
        if not self.is_valid():
            return None
        subscription = self.cleaned_data['subscription']
        name = self.cleaned_data['name']
        end = self.cleaned_data.get('date', now()) or now()
        user = ' %s' % self.connection.contact.name if self.connection.contact else ''
        subscription.end = end
        subscription.save()
        return {
            'user': user,
            'date': end,
            'name': name,
            'timeline': subscription.timeline.name,
        }
