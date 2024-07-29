import os
from celery import shared_task
from .models import AudioFile
from .utils import download_tempfile_from_url, transcribe_audio, split_large_audio


@shared_task
def transcribe_audio_task(file_url, audio_file_id):
    """
    Asynchronous task to download and transcribe audio, then update the AudioFile model.
    """
    try:
        # Download the file
        file_path = download_tempfile_from_url(file_url)
        audio_file = AudioFile.objects.get(pk=audio_file_id)

        if os.path.getsize(file_path) > 25 * 1024 * 1024:
            # Split large files into chunks
            chunks = split_large_audio(file_path)
        # Transcribe the audio
            transcription_texts = [transcribe_audio(chunk) for chunk in chunks]
            audio_file.transcription = " ".join(transcription_texts)
        else:
            audio_file.transcription = transcribe_audio(file_path)
        # Update the AudioFile model
        audio_file.save()

        # Clean up the temporary file
        os.remove(file_path)

    except Exception as e:
        print(f"Error in transcribing audio: {e}")
