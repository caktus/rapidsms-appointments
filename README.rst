RapidSMS Appointments
========================

rapidsms-appointments is a reusable RapidSMS application for sending appointment
reminders. Users can be subscribed to a timeline of milestones for future appointments. Reminders
are send to the patient or staff to remind them of the appointment. Appointments
can be confirmed or rescheduled by patient or staff. It also tracks the history of confirmed
notifications and missed/made appointments.


Dependencies
-----------------------------------

rapidsms-appointments currently runs on Python 2.6 and 2.7 and requires the following
Python packages:

- Django >= 1.4
- RapidSMS >= 0.11.0
- Celery >= 3.0.13


Documentation
-----------------------------------

Documentation on using rapidsms-appointments is available on
`Read The Docs <http://readthedocs.org/docs/rapidsms-appointments/>`_.


Running the Tests
------------------------------------

With all of the dependancies installed, you can quickly run the tests with via::

    python setup.py test

or::

    python runtests.py

To test rapidsms-appointment in multiple supported environments you can make use
of the `tox <http://tox.readthedocs.org/>`_ configuration.::

    # You must have tox installed
    pip install tox
    # Build default set of environments
    tox
    # Build a single environment
    tox -e py26-1.4.X


License
--------------------------------------

rapidsms-appointments is released under the BSD License. See the
`LICENSE <https://github.com/caktus/rapidsms-appointments/blob/master/LICENSE>`_ file for more details.


Contributing
--------------------------------------

If you think you've found a bug or are interested in contributing to this project
check out `rapidsms-appointments on Github <https://github.com/caktus/rapidsms-appointments>`_.

Development sponsored by `Caktus Consulting Group, LLC
<http://www.caktusgroup.com/services>`_.
