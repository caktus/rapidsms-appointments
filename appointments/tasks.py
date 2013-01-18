import datetime

from celery import task

from django.db.models import Q
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from rapidsms.router import send

from .models import TimelineSubscription, Appointment

APPT_REMINDER = _('This is a reminder for your upcoming appointment on %(date)s. Please confirm.')


@task()
def generate_appointments(days=14):
    """
    Task to create Appointment instances based on current TimelineSubscriptions

    Arguments:
    days: The number of upcoming days to create Appointments for
    """
    start = now()
    end = (start + datetime.timedelta(days=days)).replace(hour=23,
                                                          minute=59,
                                                          second=59)
    # get all subscriptions that haven't ended
    query = Q(end__lte=end) | Q(end__isnull=True)
    subs = TimelineSubscription.objects.filter(query)

    for sub in subs:
        milestones = sub.timeline.milestones.all()
        milestones = [x for x in milestones if \
                        sub.start + datetime.timedelta(days=x.offset) >= start \
                        and sub.start + datetime.timedelta(days=x.offset) <= end]
        # Create appointment(s) for this subscription as within the window
        for milestone in milestones:
            appt_date = sub.start + datetime.timedelta(days=milestone.offset)
            appt, created = Appointment.objects.get_or_create(
                                                    connection=sub.connection,
                                                    milestone=milestone,
                                                    date=appt_date.date())


@task()
def send_appointment_reminders(days=7):
    """
    Task to reminde connections of upcoming Appointment(s)

    Arguments:
    days: The number of upcoming days to filter upcoming Appointments
    """
    start = now()
    end = (start + datetime.timedelta(days=days)).replace(hour=23,
                                                          minute=59,
                                                          second=59)
    # get all subscriptions that haven't ended
    query = Q(date__gte=start) & Q(date__lte=end)
    appts = Appointment.objects.filter(Q(query), reminded=False)
    for appt in appts:
        send(APPT_REMINDER % {'date': appt.date}, appt.connection)
        appt.reminded = True
        appt.save()
