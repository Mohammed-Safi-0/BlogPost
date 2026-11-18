from django import forms
from .models import *
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if isinstance(data, (list, tuple)):
            return [
                super(MultipleFileField, self).clean(d, initial)
                for d in data
            ]
        else:
            return [super(MultipleFileField, self).clean(data, initial)]
class BlogForm(forms.ModelForm):
    title = forms.CharField(
        label="Blog Post title",
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter the Title of your blog post...'
        })
    )

    content = forms.CharField(
        label="Content",
        widget=forms.Textarea(attrs={
            'placeholder': 'Write your own blog post...'
        })
    )

    images = MultipleFileField(
    label='Upload images',
    required=False,
    widget=MultipleFileInput(
        attrs={'multiple': True}
    )
)

    video = forms.FileField(          
        label='Upload a video',
        required=False,
        widget=forms.ClearableFileInput()
    )

    category = forms.ModelChoiceField(
        queryset= category.objects.all(),
        required=False,
        label="Select Category",
        widget= forms.Select()
    )

    tags = forms.ModelMultipleChoiceField(
        queryset= Tag.objects.all(),
        required= False,
        label = "Select Tags",
        widget = forms.SelectMultiple()
    )

    class Meta: 
        model = BlogPost
        fields = ['title', 'content', 'category', 'tags', 'video']