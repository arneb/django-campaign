from django import forms
from django.utils.simplejson import simplejson as json
from django.utils.translation import ugettext as _

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
            raise forms.ValidationError(_(u"uploaded file must contain json data"))
        
    