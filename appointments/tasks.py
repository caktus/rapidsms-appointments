import datetime

from celery import task

from django.db.models import Q
try:
    from django.utils.timezone import now
except ImportError:  # Django < 1.4
    now = datetime.datetime.now

from .models import TimelineSubscription, Appointment


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
    #Get all subscriptions that haven't ended
    query = Q(end__lte=end) | Q(end__isnull=True)
    subs = TimelineSubscription.objects.filter(query)

    for sub in subs:
        for milestone in sub.timeline.milestones.all():
            offset = milestone.offset
            milestone_date = sub.start + datetime.timedelta(days=offset)
            #Create appointment(s) for this subscription within the task window
            if start <= milestone_date <= end:
                appt, created = Appointment.objects.get_or_create(
                                                    connection=sub.connection,
                                                    milestone=milestone,
                                                    date=milestone_date.date()
                                                    )
