=================================================
Newsletter management for the Django webframework
=================================================

Django-campaign is a newsletter campaign management app for the Django
webframework. It can manage multiple newsletters with different subscriberlists.

Features
--------

* Multiple newsletters
* Multiple subscriberlists
* Personalization of content for every Subscriber
* Subscriber model lives in your code and can have whatever fields you want
* Subscriberlists are defined as orm query parameters
* Send mails from your own Server (through Django's email mechanism)
* Send mails through Mandrill (a transactional email service from Mailchimp)
* Pluggable backends for integration with other email services
* Make newsletters available online
* Internal blacklist

Upgrading
---------

If you are upgrading from a 0.2.x release the following changes are noteworthy:

* The south migrations where removed in favor of Django 1.7 native migrations
* The 'debug' and 'django_mailer' backends are no longer used, because setting
  Django's EMAIL_BACKEND settings to the correct value has the same effect.



Documentation
-------------

The documentation is available in the docs folder and online at:
http://django-campaign.readthedocs.org

