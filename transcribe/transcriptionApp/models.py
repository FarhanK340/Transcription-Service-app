from django.db import models
from .validators import AudioFileValidator

class AudioFile(models.Model):
    title = models.CharField(max_length=50)
    audio = models.FileField(upload_to='audio/', validators=[AudioFileValidator()])
    transcription = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title