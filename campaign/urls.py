from django.conf import settings
from django.conf.urls.defaults import *

urlpatterns = patterns('campaign.views',
    url(r'^view/(?P<object_id>[\d]+)/$', 'view_online', {}, name="campaign_view_online"),
)

if getattr(settings, 'CAMPAIGN_SUBSCRIBE_CALLBACK', None):
    urlpatterns += patterns('campaign.views',
        url(r'^subscribe/$', 'subscribe', {}, name="campaign_subscribe"),
    )
    
if getattr(settings, 'CAMPAIGN_UNSUBSCRIBE_CALLBACK', None):
    urlpatterns += patterns('campaign.views',
        url(r'^unsubscribe/$', 'unsubscribe', {}, name="campaign_unsubscribe"),
    )