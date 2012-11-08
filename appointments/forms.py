from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import Timeline


class NewMessageForm(forms.Form):
    "Validate data parsed from incoming messages."

    keyword = forms.CharField()
    name = forms.CharField()
    date = forms.DateField(required=False)

    def clean_keyword(self):
        "Check if this keyword is associated with any timeline."
        keyword = self.cleaned_data.get('keyword', '')
        match = None
        if keyword:
            # Query DB for valid keywords
            for timeline in Timeline.objects.filter(slug__icontains=keyword):
                if keyword.strip().lower() in timeline.keywords:
                    match = timline
                    break
        if match is None:
            # Invalid keyword
            raise forms.ValidationError(_('Unknown keyword.'))
        else:
            self.cleaned_data['timeline'] = match
        return keyword
