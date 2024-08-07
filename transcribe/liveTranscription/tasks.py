import os
from celery import shared_task
from whisper import load_model


@shared_task
def transcribe_audio_chunk(bytes_data, session_name):
    """
    Asynchronous task to transcribe audio.

    Args:
        bytes_data (bytes): The audio data in bytes.
        session_name (str): The name of the session used to generate the file name.

    Returns:
        str: The transcribed text from the audio file.

    Raises:
        Exception: If an error occurs during transcription.
    """
    try:
        # Load Whisper model
        model = load_model('base')

        # Get Path to Desktop where audio file will be stored.
        PERMANENT_FILE_PATH = os.path.join(os.path.join(
            os.path.expanduser("~"), "Desktop"), f"{session_name}.wav")

        # Append the bytes to the permanent file
        with open(PERMANENT_FILE_PATH, 'ab') as perm_file:
            perm_file.write(bytes_data)

        # Transcribe the permanent file
        transcription_result = model.transcribe(
            PERMANENT_FILE_PATH, language='en')

        return transcription_result['text']
    except Exception as e:
        error_message = f"Failed to transcribe audio file: {
            PERMANENT_FILE_PATH}. Error: {str(e)}"
        print(error_message)
        raise Exception(error_message)
