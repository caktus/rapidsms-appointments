from django.contrib import admin
from appointments.models import Timeline, TimelineSubscription, Milestone, Appointment, Notification

admin.site.register(Timeline)
admin.site.register(TimelineSubscription)
admin.site.register(Milestone)
admin.site.register(Appointment)
admin.site.register(Notification)
