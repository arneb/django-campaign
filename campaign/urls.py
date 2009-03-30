from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^(?P<object_id>[\d]+)/$', 'campaign.views.view_online', {}, name="campaign_view_online"),
)