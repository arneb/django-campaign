from django.conf import settings
from django.urls import re_path
from campaign.views import view_online, subscribe, unsubscribe


urlpatterns = [
    re_path(r'^view/(?P<object_id>[\d]+)/$', view_online, {}, name="campaign_view_online"),
]

if getattr(settings, 'CAMPAIGN_SUBSCRIBE_CALLBACK', None):
    urlpatterns += [
        re_path(r'^subscribe/$', subscribe, {}, name="campaign_subscribe"),
    ]

if getattr(settings, 'CAMPAIGN_UNSUBSCRIBE_CALLBACK', None):
    urlpatterns += [
        re_path(r'^unsubscribe/$', unsubscribe, {}, name="campaign_unsubscribe"),
    ]
