import os
import tempfile
import uuid
from celery import shared_task
from whisper import load_model
from channels.db import database_sync_to_async
from .models import Session, Transcription


@shared_task
def transcribe_audio_chunk(bytes_data, context, session_name):
    """
    Asynchronous task to transcribe audio.
    """
    try:
        model = load_model('base')
    
        # Save the audio chunk temporarily to disk
        with tempfile.NamedTemporaryFile(delete=False, prefix=session_name, suffix=".webm") as temp_audio_file:
            temp_audio_file.write(bytes_data)
            temp_audio_file.flush()
            temp_audio_file_path = temp_audio_file.name

        if not os.path.isfile(temp_audio_file_path) or os.path.getsize(temp_audio_file_path) == 0:
            raise Exception(f"Temporary file not created or is empty: {temp_audio_file_path}")

        transcription_result = model.transcribe(
            temp_audio_file_path, language='en', initial_prompt=context)
        os.remove(temp_audio_file_path)

        return transcription_result['text']
    except Exception as e:
        error_message = f"Failed to transcribe audio file: {
            temp_audio_file_path}. Error: {str(e)}"
        print(error_message)
        raise Exception(error_message)