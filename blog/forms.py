#blog/forms.py
from django import forms
from .models import BlogComment

class BlogPostForm(forms.Form):
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Post title'}))
    intro = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':3, 'placeholder': 'Short intro (optional)'}))
    body = forms.CharField(widget=forms.Textarea(attrs={'rows':12, 'placeholder': 'Write your post here...'}))
    publish = forms.BooleanField(required=False, initial=False,
                                 help_text="Publish immediately (staff only).")

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = BlogComment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add your comment...'}),
        }
