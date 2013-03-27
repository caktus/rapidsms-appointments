"""Test URL configuration."""

from __future__ import unicode_literals

# for Django 1.3 support
try:
    from django.conf.urls import patterns, include
except ImportError:
    from django.conf.urls.defaults import patterns, include


urlpatterns = patterns('',
    (r'^', include('appointments.urls')),
    (r'^', include('rapidsms.urls.login_logout')),
)
