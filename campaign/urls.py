from django.conf import settings
from django.conf.urls import url
from campaign.views import view_online, subscribe, unsubscribe

urlpatterns = [
    url(r'^view/(?P<object_id>[\d]+)/$', view_online, {}, name="campaign_view_online"),
]

if getattr(settings, 'CAMPAIGN_SUBSCRIBE_CALLBACK', None):
    urlpatterns += [
        url(r'^subscribe/$', subscribe, {}, name="campaign_subscribe"),
    ]

if getattr(settings, 'CAMPAIGN_UNSUBSCRIBE_CALLBACK', None):
    urlpatterns += [
        url(r'^unsubscribe/$', unsubscribe, {}, name="campaign_unsubscribe"),
    ]
