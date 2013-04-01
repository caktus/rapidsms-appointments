Getting Started
====================================

Here you will find the necessary steps to install and initial configure the
rapidsms-appointments application.


Requirements
------------------------------------

rapidsms-appointments requires Python 2.6 or 2.7. Python 3 is not currently supported but is
planned in the future as Django and RapidSMS support for Python 3 increases. It also requires
the following packages:

* `Django <https://www.djangoproject.com/>`_ >= 1.4
* `RapidSMS <http://www.rapidsms.org/>`_ >= 0.12
* `Celery <http://www.celeryproject.org/>`_ >= 3.0


Installation
------------------------------------

Stable releases of rapidsms-appointments can be found on `PyPi <http://pypi.python.org/>`_
and `pip <http://www.pip-installer.org/>`_ is the recommended method for installing the package::

    pip install rapidsms-appointments

Once installed you should add ``appointments`` to your ``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        # Required apps
        'rapidsms',
        'rapidsms.contrib.handlers',
        # Other apps go here
        'appointments',
    )

To create the necessary tables for the appointment data via::

    python manage.py syncdb

rapidsms-appointments is compatible with `South <http://south.aeracode.org/>`_ and if
you are using South to handle schemamigrations then instead you should run::

    python manage.py migrate appointments


Configuration
------------------------------------

As noted in the above requirements, rapidsms-appointments uses Celery to manage periodic
tasks such as sending reminders for upcoming appointments. There are two tasks which you
should add to your ``CELERYBEAT_SCHEDULE`` configuration::

    from celery.schedules import crontab

    CELERYBEAT_SCHEDULE = {
        'generate-appointments': {
            'task': 'appointments.tasks.generate_appointments',
            'schedule': crontab(hour=0, minute=0, day_of_week=1), # Every monday at midnight
        },
        'send-notifications': {
            'task': 'appointments.tasks.send_appointment_notifications',
            'schedule': crontab(hour=12, minute=0), # Every day at noon
        },
    }

These schedules are for example purposes and can be customized for your deployments needs.
For a complete reference on integrating Celery in a Django project you should
see the `Celery documentation <http://docs.celeryproject.org/en/latest/django/index.html>`_.


Next Steps
------------------------------------

Continue reading to the :doc:`project overview </overview>` to learn about the terminology
used and how you can define the set of appointments for your project.
