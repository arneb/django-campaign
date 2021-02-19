from __future__ import unicode_literals

from django.shortcuts import render
from django import template
from django import forms
try:
    from django.utils.functional import update_wrapper
except ImportError:
    from functools import update_wrapper
from django.conf.urls import url
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.utils import unquote
from django.contrib.admin.options import IS_POPUP_VAR
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from campaign.forms import SubscriberListForm
from campaign.models import (
    BlacklistEntry, Campaign, MailTemplate, Newsletter, SubscriberList
)


class CampaignAdmin(admin.ModelAdmin):
    filter_horizontal=('recipients',)
    list_display=('name', 'newsletter', 'sent', 'sent_at', 'online')
    change_form_template = "admin/campaign/campaign/change_form.html"
    send_template = None

    def has_send_permission(self, request, obj):
        """
        Subclasses may override this and implement more granular permissions.
        """
        return request.user.has_perm("campaign.send_campaign")


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
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(opts.verbose_name), 'key': escape(object_id)})

        if request.method == 'POST':
            if not request.POST.get('send', None) == '1':
                raise PermissionDenied

            num_sent = obj.send()
            messages.success(request, _('The %(name)s "%(obj)s" was successfully sent. %(num_sent)s messages delivered.' %  {'name': force_text(opts.verbose_name), 'obj': force_text(obj), 'num_sent': num_sent,}))
            return HttpResponseRedirect('../')


        def form_media():
            css = ['css/forms.css',]
            return forms.Media(css={'screen': ['%sadmin/%s' % (settings.STATIC_URL, url) for url in css]})

        media = self.media + form_media()

        context = {
            'title': _('Send %s') % force_text(opts.verbose_name),
            'object_id': object_id,
            'object': obj,
            'is_popup': (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            'media': mark_safe(media),
            'app_label': opts.app_label,
            'opts': opts,
        }
        context.update(extra_context or {})

        return render(request, self.send_template or
            ['admin/campaign/%s/send_object.html' % (opts.object_name.lower()),
            'admin/campaign/send_object.html',
            'admin/send_object.html'], context)


    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        super_urlpatterns = super(CampaignAdmin, self).get_urls()
        urlpatterns = [
            url(r'^(.+)/send/$',
                wrap(self.send_view),
                name='%s_%s_send' % info),
        ]
        urlpatterns += super_urlpatterns

        return urlpatterns


class BlacklistEntryAdmin(admin.ModelAdmin):
    list_display=('email', 'added')
    changelist_template = "admin/campaign/blacklistentry/change_list.html"

    def fetch_mandrill_rejects(self, request):
        call_command('fetch_mandrill_rejects')
        msg = _("Successfully fetched Mandrill rejects")
        self.message_user(request, msg, messages.SUCCESS)
        return HttpResponseRedirect(request.META.get("HTTP_REFERER", '..'))


    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        super_urlpatterns = super(BlacklistEntryAdmin, self).get_urls()
        urlpatterns = [
            url(r'^fetch_mandrill_rejects/$',
                wrap(self.fetch_mandrill_rejects),
                name='%s_%s_fetchmandrillrejects' % info),
        ]
        urlpatterns += super_urlpatterns

        return urlpatterns


class SubscriberListAdmin(admin.ModelAdmin):
    form = SubscriberListForm
    change_form_template = "admin/campaign/subscriberlist/change_form.html"
    preview_template = None

    def preview_view(self, request, object_id, extra_context=None):
        """
        Allows to view a preview of selected susbcribers.
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

        if obj is None:
            raise Http404(_('%(name)s object with primary key %(key)r does not exist.') % {'name': force_text(opts.verbose_name), 'key': escape(object_id)})

        context = {
            'title': _('Preview %s') % force_text(opts.verbose_name),
            'object_id': object_id,
            'object': obj,
            'is_popup': (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
            'media': mark_safe(self.media),
            'app_label': opts.app_label,
            'opts': opts,
        }
        context.update(extra_context or {})

        return render(request, self.preview_template or
            ['admin/campaign/%s/preview.html' % (opts.object_name.lower()),
            'admin/campaign/preview.html',
            'admin/preview.html'], context)

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        super_urlpatterns = super(SubscriberListAdmin, self).get_urls()
        urlpatterns = [
            url(r'^(.+)/preview/$',
                wrap(self.preview_view),
                name='%s_%s_preview' % info),
        ]
        urlpatterns += super_urlpatterns

        return urlpatterns


admin.site.register(Campaign, CampaignAdmin)
admin.site.register(BlacklistEntry, BlacklistEntryAdmin)
admin.site.register(SubscriberList, SubscriberListAdmin)
admin.site.register(MailTemplate)
admin.site.register(Newsletter, list_display=('name', 'from_email', 'from_name'))
