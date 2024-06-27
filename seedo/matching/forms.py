# matching/forms.py

from django import forms


class SendRequestForm(forms.Form):
    email = forms.EmailField(label="Recipient Email")
