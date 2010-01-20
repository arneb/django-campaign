from django import template, http
from django.conf import settings
from django.shortcuts import get_object_or_404, render_to_response
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from campaign.models import Campaign, BlacklistEntry
from campaign.forms import SubscribeForm, UnsubscribeForm

def view_online(request, object_id):
    campaign = get_object_or_404(Campaign, pk=object_id, online=True)
    
    if campaign.template.html is not None and \
        campaign.template.html != u"" and \
        not request.GET.get('txt', False):
        tpl = template.Template(campaign.template.html)
        content_type = 'text/html; charset=utf-8'
    else:
        tpl = template.Template(campaign.template.plain)
        content_type = 'text/plain; charset=utf-8'
    context = template.Context({})
    if campaign.online:
        context.update({'view_online_url': reverse("campaign_view_online", kwargs={'object_id': campaign.pk}),
                        'viewed_online': True,
                        'site_url': Site.objects.get_current().domain})    
    return http.HttpResponse(tpl.render(context), 
                            content_type=content_type)
        


def subscribe(request, template_name='campaign/subscribe.html', 
              form_class=SubscribeForm, extra_context=None):
    context = extra_context or {}
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            callback = _get_callback('CAMPAIGN_SUBSCRIBE_CALLBACK')
            if callback:
                success = callback(form.cleaned_data['email'])
                context.update({'success': success, 'action': 'subscribe'})
            else:
                raise ImproperlyConfigured("CAMPAIGN_SUBSCRIBE_CALLBACK must be configured to use the subscribe view")
    else:
        form = form_class()
    context.update({'form': form})
    return render_to_response(template_name, context, 
                        context_instance=template.RequestContext(request))

    
def unsubscribe(request, template_name='campaign/unsubscribe.html',
                form_class=UnsubscribeForm, extra_context=None):
    context = extra_context or {}
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            callback = _get_callback('CAMPAIGN_UNSUBSCRIBE_CALLBACK')
            if callback:
                success = callback(form.cleaned_data['email'])
                context.update({'success': success, 'action': 'unsubscribe'})
            else:
                raise ImproperlyConfigured("CAMPAIGN_UNSUBSCRIBE_CALLBACK must be configured to use the unsubscribe view")
    else:
        initial = {}
        if request.GET.get('email'):
            initial['email'] = request.GET.get('email')
        form = form_class(initial=initial)
    context.update({'form': form})
    return render_to_response(template_name, context, 
                        context_instance=template.RequestContext(request))


def _get_callback(setting):
    callback = getattr(settings, setting, None)
    if callback is None:
        return None
    if callable(callback):
        return callback
    else:
        mod, name = callback.rsplit('.', 1)
        module = __import__(mod, {}, {}, [''])
        return getattr(module, name)
    
        
                