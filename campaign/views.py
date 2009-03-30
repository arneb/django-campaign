from django import template, http
from django.shortcuts import get_object_or_404
from campaign.models import Campaign

def view_online(request, object_id):
    campaign = get_object_or_404(Campaign, pk=object_id, online=True)
    
    if campaign.template.html is not None and campaign.template.html != u"":
        tpl = template.Template(campaign.template.html)
        content_type = 'text/html, charset=utf-8'
    else:
        tpl = template.Template(campaign.template.plain)
        content_type = 'text/plain, charset=utf-8'
        
    return http.HttpResponse(tpl.render(template.Context({})), content_type=content_type)
        
    