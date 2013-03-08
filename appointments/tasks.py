import datetime

from celery import task

from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
try:
    from django.utils.timezone import now
except ImportError:  # Django < 1.4
    now = datetime.datetime.now

from rapidsms.router import send

from .models import TimelineSubscription, Appointment, Notification

APPT_REMINDER = _('This is a reminder for your upcoming appointment on %(date)s. Please confirm.')


@task()
def generate_appointments(days=14):
    """
    Task to create Appointment instances based on current TimelineSubscriptions

    Arguments:
    days: The number of upcoming days to create Appointments for
    """
    start = datetime.date.today()
    end = start + datetime.timedelta(days=days)

    query = Q(end__gte=start) | Q(end__isnull=True)
    subs = TimelineSubscription.objects.filter(query)

    for sub in subs:
        for milestone in sub.timeline.milestones.all():
            milestone_date = sub.start.date() + datetime.timedelta(days=milestone.offset)
            #Create appointment(s) for this subscription within the task window
            if start <= milestone_date <= end:
                appt, created = Appointment.objects.get_or_create(
                                                    connection=sub.connection,
                                                    milestone=milestone,
                                                    date=milestone_date
                                                    )


@task()
def send_appointment_notifications(days=7):
    """
    Task to send reminders notifications for upcoming Appointment

    Arguments:
    days: The number of upcoming days to filter upcoming Appointments
    """
    start = datetime.date.today()
    end = start + datetime.timedelta(days=days)

    # get all subscriptions that haven't ended
    query = Q(date__gte=start) & Q(date__lte=end)
    blacklist = [Notification.STATUS_SENT, Notification.STATUS_CONFIRMED, Notification.STATUS_MANUAL]
    appts = Appointment.objects.filter(query).exclude(notifications__status__in=blacklist)
    for appt in appts:
        msg = APPT_REMINDER % {'date': appt.date}
        send(msg, appt.connection)
        Notification.objects.create(appointment=appt,
                                    status=Notification.STATUS_SENT,
                                    sent=now(),
                                    message=msg)
