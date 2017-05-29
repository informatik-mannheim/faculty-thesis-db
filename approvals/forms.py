from django import forms


class RejectForm(forms.Form):
    reason_widget = forms.Textarea(attrs={'cols': 40, 'rows': 5})

    reason = forms.CharField(label="Begründung",
                             max_length=2000,
                             required=True,
                             strip=True,
                             widget=reason_widget)
