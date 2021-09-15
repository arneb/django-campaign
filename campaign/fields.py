import json

from django import forms
from django.conf import settings
from django.db import models


class JSONWidget(forms.Textarea):
    def render(self, name, value, attrs=None, renderer=None):
        if not isinstance(value, str):
            value = json.dumps(value, indent=2)
        return super().render(name, value, attrs)


class JSONFormField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = JSONWidget
        super().__init__(*args, **kwargs)

    def clean(self, value):
        if not value: return
        try:
            return json.loads(value)
        except Exception as exc:
            raise forms.ValidationError('JSON decode error: %s' % (str(exc),))


class JSONField(models.TextField):
    def formfield(self, **kwargs):
        return super().formfield(form_class=JSONFormField, **kwargs)

    def to_python(self, value):
        if isinstance(value, str):
            value = json.loads(value)
        return value

    def from_db_value(self, value, expression, connection, context):
        if isinstance(value, str):
            value = json.loads(value)
        return value

    def get_db_prep_save(self, value, connection=None):
        if value is not None:
            return json.dumps(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)
