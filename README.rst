==========================================================
Newsletter campaign management for the Django webframework
==========================================================

Django-campaign is a newsletter campaign management app for the Django
webframework. It can manage multiple newsletters with different subscriberlists.


Upgrading
---------

If you are upgrading from a 0.2.x release the following changes are noteworthy:

* The south migrations where removed in favor of Django 1.7 native migrations

* The 'debug' and 'django_mailer' backends are no longer used, because setting
  Django's EMAIL_BACKEND settings to the correct value has the same effect.

*


Documentation
-------------

The documentation is available in the docs folder and online at:
http://django-campaign.readthedocs.org

