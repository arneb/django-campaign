from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist, FieldError
from django.utils.module_loading import import_string
from django.utils.translation import ugettext as _

from campaign.models import SubscriberList


class SubscribeForm(forms.Form):
    email = forms.EmailField()


class UnsubscribeForm(forms.Form):
    email = forms.EmailField()


class SubscriberListForm(forms.ModelForm):
    class Meta:
        model = SubscriberList
        exclude = ()

    def clean(self):
        super().clean()

        content_type = self.cleaned_data.get("content_type")
        email_field_name = self.cleaned_data.get("email_field_name")
        filter_condition = self.cleaned_data.get("filter_condition")
        custom_list = self.cleaned_data.get("custom_list")

        if not custom_list and not all([content_type, filter_condition]):
            self.add_error(None, _("Either custom_list or content_type and filter_condition must be set"))

        if custom_list:  # Check if the defined module does exist and can be initialized, if not throw a hard exception instead of only adding an error
            import_string(custom_list)()
        else:
            Model = content_type.model_class()

            try:
                Model._meta.get_field(email_field_name)
            except FieldDoesNotExist:
                self.add_error(
                    "email_field_name",
                    _("Field not found on selected %s") % ContentType._meta.verbose_name
                )

            try:
                Model._default_manager.filter(**{str(k): v for k, v in filter_condition.items()})
            except FieldError:
                self.add_error(
                    "filter_condition",
                    _("Could not query %s with this filter") % ContentType._meta.verbose_name
                )
