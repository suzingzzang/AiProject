from django import forms

from .models import QnA


class QnAForm(forms.ModelForm):
    class Meta:
        model = QnA
        fields = ["title", "content"]
        labels = {"title": "제목", "content": "내용"}


class CommentForm(forms.ModelForm):
    content = forms.CharField(widget=forms.Textarea, label="Comment")

    class Meta:
        model = QnA
        fields = ["content"]
