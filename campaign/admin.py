import csv
from django import forms
from django.shortcuts import render_to_response
from django import template
from django.utils.functional import update_wrapper
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.contrib.admin.util import unquote
from django.core.exceptions import PermissionDenied
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
try:
    from django.utils.simplejson import simplejson as json
except ImportError:
    from django.utils import simplejson as json

from campaign.models import MailTemplate, Subscriber, Campaign, BlacklistEntry, BounceEntry, SubscriberList
from campaign.forms import UploadForm


class SubscriberAdmin(admin.ModelAdmin):
    
    import_template=None
    list_display = ('email', 'salutation')
    
    def has_import_permission(self, request):
        """
        TODO: integrate with django's permission system
        """
        return request.user.is_superuser
        
    def import_view(self, request, extra_context=None):
        """
        Import email addresses and salutation from a uploaded text file.
        """
        model = self.model
        opts = model._meta
        
        if not self.has_import_permission(request):
            raise PermissionDenied

        if request.method == 'POST':
            form = UploadForm(request.POST, request.FILES)
            if form.is_valid():
                num_import = 0

                try: # try json
                    data = json.loads(form.cleaned_data['file'].read())

                    for entry in data:
                        try:
                            Subscriber.objects.create(email=entry['email'], salutation=force_unicode(entry['name']))
                            num_import += 1
                        except Exception, e:
                            pass
                except: # may be csv data
                    try:
                        reader = csv.reader(form.cleaned_data['file'].readlines(), delimiter=',')
                        for entry in reader:
                            try:
                                Subscriber.objects.create(email=entry[0], salutation=force_unicode(entry[1]))
                                num_import += 1
                            except Exception, e:
                                pass
                    except:
                        raise
                                
                request.user.message_set.create(message=_(u'Successfully imported  %(num_import)s %(name)s.' %  {'name': force_unicode(opts.verbose_name_plural), 'num_import': num_import,}))
                return HttpResponseRedirect('../')
                        
        else:
            form = UploadForm()

        def form_media():
            from django.conf import settings
            css = ['css/forms.css',]
            return forms.Media(css={'screen': ['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url) for url in css]})

        media = self.media + form_media()
        context = {
            'title': _('Import %s') % force_unicode(opts.verbose_name_plural),
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': mark_safe(media),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
            'opts': opts,
            'form': form,
        }

        context.update(extra_context or {})
        return render_to_response(self.import_template or
            ['admin/%s/%s/import.html' % (opts.app_label, opts.object_name.lower()),
            'admin/%s/import.html' % opts.app_label,
            'admin/import.html'], context, context_instance=template.RequestContext(request))

    
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name

        super_urlpatterns = super(SubscriberAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r'^import/$',
                wrap(self.import_view),
                name='%sadmin_%s_%s_import' % info),
        )
        urlpatterns += super_urlpatterns

        return urlpatterns    

class CampaignAdmin(admin.ModelAdmin):
    filter_horizontal=('recipients',)
    list_display=('name', 'sent', 'online')
    send_template = None
    
    def has_send_permission(self, request, obj):
        """
        Subclasses may override this and implement more granular permissions.
        TODO: integrate with django's permisson system
        """
        return request.user.is_superuser
        
        
    def send_view(self, request, object_id, extra_context=None):
        """
        Allows the admin to send out the mails for this campaign.
        """
        model = self.model
        opts = model._meta
        
        try:
            obj = model._default_manager.get(pk=unquote(object_id))
        except model.DoesNotExist:
            # Don't raise Http404 just yet, because we haven't checked
            # permissions yet. We don't want an unauthenticated user to be able
            # to determine whether a given object exists.
            obj = None
        
        if not self.has_send_permission(request, obj):
            raise PermissionDenied
        
        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_unicode(opts.verbose_name), 'key': escape(object_id)})
        
        if request.method == 'POST':
            if not request.POST.get('send', None) == '1':
                raise PermissionDenied
            
            num_sent = obj.send()
            request.user.message_set.create(message=_(u'The %(name)s "%(obj)s" was successfully sent. %(num_sent)s messages delivered.' %  {'name': force_unicode(opts.verbose_name), 'obj': force_unicode(obj), 'num_sent': num_sent,}))
            return HttpResponseRedirect('../')

        
        def form_media():
            from django.conf import settings
            css = ['css/forms.css',]
            return forms.Media(css={'screen': ['%s%s' % (settings.ADMIN_MEDIA_PREFIX, url) for url in css]})
        
        media = self.media + form_media()

        context = {
            'title': _('Send %s') % force_unicode(opts.verbose_name),
            'object_id': object_id,
            'object': obj,
            'is_popup': request.REQUEST.has_key('_popup'),
            'media': mark_safe(media),
            'root_path': self.admin_site.root_path,
            'app_label': opts.app_label,
            'opts': opts,
        }
        context.update(extra_context or {})
        
        return render_to_response(self.send_template or
            ['admin/%s/%s/send_object.html' % (opts.app_label, opts.object_name.lower()),
            'admin/%s/send_object.html' % opts.app_label,
            'admin/send_object.html'], context, context_instance=template.RequestContext(request))
    
        
    def get_urls(self):
        from django.conf.urls.defaults import patterns, url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.admin_site.name, self.model._meta.app_label, self.model._meta.module_name
        
        super_urlpatterns = super(CampaignAdmin, self).get_urls()
        urlpatterns = patterns('',
            url(r'^(.+)/send/$',
                wrap(self.send_view),
                name='%sadmin_%s_%s_send' % info),
        )
        urlpatterns += super_urlpatterns
        
        return urlpatterns


admin.site.register(Campaign, CampaignAdmin)
admin.site.register(MailTemplate)
admin.site.register(Subscriber, SubscriberAdmin)
admin.site.register(BlacklistEntry)
admin.site.register(BounceEntry)
admin.site.register(SubscriberList, filter_horizontal=('subscribers',))
