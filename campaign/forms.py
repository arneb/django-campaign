import csv
from django import forms
from django.utils.translation import ugettext as _
try:
    from django.utils.simplejson import simplejson as json
except ImportError:
    from django.utils import simplejson as json
    
class UploadForm(forms.Form):
    """
    validates that the uploaded file contains parseable json data.
    """
    file = forms.FileField()
    
    def clean_file(self):
        try:
            json.loads(self.cleaned_data['file'].read())
            self.cleaned_data['file'].seek(0)
            return self.cleaned_data['file']
        except Exception, e:
            try:
                reader = csv.reader(self.cleaned_data['file'].readlines())
                self.cleaned_data['file'].seek(0)
                return self.cleaned_data['file']
            except Exception, e:
                raise forms.ValidationError(_(u"uploaded file must contain json or csv data"))
        
