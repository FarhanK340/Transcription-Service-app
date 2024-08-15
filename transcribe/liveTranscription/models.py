from django.db import models


class Session(models.Model):
    session_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_name

class Transcription(models.Model):
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
    )
    transcription = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.transcription
