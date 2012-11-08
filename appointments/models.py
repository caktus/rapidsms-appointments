from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
try:
    from django.utils.timezone import now
except ImportError: # Django < 1.4
    now = datetime.datetime.now


class Timeline(models.Model):
    "A series of milestones which users can subscribe for milestone reminders."

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, help_text=_('The keyword(s) to match '
        'in messages from the user. Specify multiple keywords by separating them '
        'with vertical bars. e.g., "birth|bith|bilth"'))

    def __unicode__(self):
        return self.name


class TimelineSubscription(models.Model):
    "Subscribing a user to a timeline of reminders."

    timeline = models.ForeignKey(Timeline, related_name='subscribers')
    connection = models.ForeignKey('rapidsms.Connection', related_name='timelines')
    pin = models.CharField(max_length=160, help_text=_('Name, phrase, or digits used when joining the timeline.'))
    start = models.DateTimeField(_('start date'), default=now)
    end = models.DateTimeField(_('end date'), default=None)

    def __unicode__(self):
        return '%s - %s' % (self.contact, self.timeline) 


class Milestone(models.Model):
    "A point on the timeline that needs an appointment."

    name = models.CharField(max_length=255)
    timeline = models.ForeignKey(Timeline, related_name='milestones')
    offset = models.IntegerField()

    def __unicode__(self):
        return self.name


class Appointment(models.Model):
    "Instance of a subscribed user hitting a milestone."

    milestone = models.ForeignKey(Milestone, related_name='appointments')
    connection = models.ForeignKey('rapidsms.Connection', related_name='appointments')
    date = models.DateField(_('appointment date'))
    confirmed = models.DateTimeField(blank=True, null=True, default=None)
    reschedule = models.ForeignKey('self', blank=True, null=True, related_name='appointments')
    missed = models.BooleanField(default=True, blank=True)
    notes = models.CharField(max_length=160, blank=True, default='')

    def __unicode__(self):
        return 'Appointment for %s on %s' % (self.contact, self.date.isoformat()) 


class Notification(models.Model):
    "Record of user notification for an appointment."

    STATUS_SENT =  1
    STATUS_CONFIRMED = 2
    STATUS_MANUAL = 3
    STATUS_ERROR = 4

    STATUS_CHOICES = (
        (STATUS_SENT, _('Sent')),
        (STATUS_CONFIRMED, _('Confirmed')),
        (STATUS_MANUAL, _('Manually Confirmed')),
        (STATUS_ERROR, _('Error')),
    )

    appointment = models.ForeignKey(Appointment, related_name='notifications')
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_SENT)
    sent = models.DateTimeField(blank=True, null=True, default=now)
    confirmed = models.DateTimeField(blank=True, null=True, default=None)
    message = models.CharField(max_length=160)

    def __unicode__(self):
        return 'Notification for %s on %s' % (self.contact, self.sent.isoformat()) 
