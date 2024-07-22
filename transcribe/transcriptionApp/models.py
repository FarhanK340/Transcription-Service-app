from django.db import models

# Create your models here.

class AudioFile(models.Model):
    title = models.CharField(max_length=50)    
    audio = models.FileField(upload_to='audio/')
    transcription = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title