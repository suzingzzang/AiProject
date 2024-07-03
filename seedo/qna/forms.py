from django import forms

from .models import QnA


class QnAForm(forms.ModelForm):
    class Meta:
        model = QnA
        fields = ["title", "content"]


class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, label="Comment")

    class Meta:
        model = QnA
        fields = ["content"]
