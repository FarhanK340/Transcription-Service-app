from django import forms
from .models import AudioFile


class AudioFileForm(forms.ModelForm):
    class Meta:
        model = AudioFile
        fields = ['title', 'audio']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'flex w-full p-2 border border-gray-300 rounded-md border-none outline-none',
                'placeholder':'Enter Audio Title'
            }),
            'audio': forms.ClearableFileInput(attrs={
                'class':'class:flex w-full p-1 border border-gray-300 bg-gray-100 rounded-md border-none outline-none',
            }),
        }
