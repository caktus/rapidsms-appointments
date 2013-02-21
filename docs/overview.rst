Project Overview
====================================

rapidsms-appointments allows users to subscribe to a timeline of future appointments. These
timelines and their related milestones are defined in the database. Appointments are
scheduled relative to the user joining the timeline and they are sent a reminder
just prior to the appointment.


Defining Appointments
------------------------------------

Below is a description of the terminology used in this project and a high level
overview of the underlying data model. There are two primary models that you need
to manage in the admin for defining your set of appointments: :ref:`Timeline` and :ref:`Milestone`.
The other models are noted here but are primarily managed through the application workflow.


.. _Timeline:

Timeline
____________________________________

A timeline is the top-level structure for appointments. Each timeline has a set
of keywords that the user can use to subscribe to the timeline.


.. _Milestone:

Milestone
____________________________________

A milestone is a point on a timeline which requires an appointment. Milestones
are relative to a user joining the timeline. For instance you might have a timeline
to track pregancies. The milestones would correspond to appointments throughout the
pregancy (6 weeks, 12 weeks, 18 weeks, etc).


.. _TimelineSubscription:

TimelineSubscription
____________________________________

A TimelineSubscription attaches a User to a particular Timeline, and is the basis
for generating Appointments based on the Timeline's Milestones.


.. _Appointment:

Appointment
____________________________________

An appointment is a record of a user who is subscribed to a timeline hitting a particular
milestone. Appointments might be made or missed by the user. They could also be
rescheduled.


.. _Notification:

Notification
____________________________________

When a user has an upcoming appointment they will recieve on or more notifications to
serve as a reminder. A user can confirm they recieved the nofication or not.


.. _Workflow:

Workflow
------------------------------------

Below describes a sample workflow for creating the timeline and milestone data
and the using the SMS interactions. This example will track a set of appointments
for a new born baby.

First a site admin will create a timeline with a keyword 'birth' and a name 'New Birth'.
Associated with that timeline they will create milestones at 1 week (7 days), 2 weeks (14 days),
1 month (30 days), 3 months (90 days), 6 months (180 days), and 1 year (365 days).

To subscribe to these notifications a user will send in an SMS with the message::

    APPT NEW BIRTH Joe

where ``Joe`` is the name of the child. In place of the name they might also use a patient
idenifier such as ``ID123``. This name/id will be used for future confirmations.

One week later the user will have hit the first milestone and they will be sent a
reminder over SMS. Once they have recieved they can confirm they read it by sending
back::

    APPT CONFIRM Joe

Again ``Joe`` might be replaced with another identifier, whichever was used for the
original subscription.

Once the appointment has passed the user can mark that the appointment was made
or missed::

    APPT STATUS Joe SAW
    APPT STATUS Joe MISSED

Appointments can also be reschuduled via::

    APPT MOVE Joe <Date>

where ``<DATE>`` denotes the new appointment date. A new reminder will be sent for
the new appointment.

A user can be unsubscribed from a TimelineSubscription, and will no longer receive notifications for said subscription::

    APPT QUIT BIRTH Joe <Date>

where  ``<DATE>`` denotes the day on which the subscription should end. This field is optional
and defaults to the date which the QUIT message was sent.