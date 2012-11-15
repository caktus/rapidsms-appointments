from __future__ import unicode_literals

from django import forms
from django.db.models import Q
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy as _

from .models import Timeline, Appointment, Notification, now


class NewForm(forms.Form):
    "Register user for new timeline."

    keyword = forms.CharField()
    name = forms.CharField()
    date = forms.DateField(required=False)

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
            raise forms.ValidationError(_('Unknown keyword.'))
        else:
            self.cleaned_data['timeline'] = match
        return keyword


class PlainErrorList(forms.ErrorList):
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
                if field in self.errors:
                    error = self.errors[field].as_text()
                    break
            if error is None and forms.NON_FIELD_ERRORS in self.errors:
                error = self.errors[forms.NON_FIELD_ERRORS].as_text()
        return error


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
            raise forms.ValidationError(_('Name/ID does not match an active subscription.'))
        try:
            notification = Notification.objects.filter(
                status=Notification.STATUS_SENT,
                confirmed__isnull=True,
                appointment__confirmed__isnull=True,
                appointment__reschedule__isnull=True,
                appointment__date__lt=now(),
                milestone__timeline__in=timelines
            ).order_by('-sent')[0]
        except IndexError:
            # No unconfirmed notifications
            raise forms.ValidationError(_('You have no unconfirmed appointment notifications.'))
        else:
            self.cleaned_data['notification'] = notification
        return name

    def save(self):
        "Mark the current notification as confirmed and return it."
        if not self.is_valid():
            return None
        notification = self.cleaned_data['notification']
        notification.confirm()
        return notification

