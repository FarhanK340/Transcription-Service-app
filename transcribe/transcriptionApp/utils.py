import tempfile
import requests
from pydub import AudioSegment
from whisper import transcribe, load_model


def download_tempfile_from_url(url):
    """
    Download a file from the given URL and save it to a temporary file
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
    except requests.RequestException as e:
        raise Exception(f'Failed to download the file from the URL: ',
                        '{url}. Error: {e}')
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        for chunk in response.iter_content(chunk_size=4 * 1024 * 1024):
            temp_file.write(chunk)
        temp_file_path = temp_file.name
        return temp_file_path


def split_large_audio(file_path, max_size_mb=25):
    """
    Split audio files larger than max_size_mb into smaller chunks.
    """
    audio = AudioSegment.from_file(file_path)
    chunks = []
    chunk_size = max_size_mb * 1024 * 1024
    duration_ms = len(audio)
    chunk_duration_ms = chunk_size / (audio.frame_rate * audio.frame_width)

    for i in range(0, duration_ms, chunk_duration_ms):
        chunk = audio[i:i + chunk_duration_ms]
        chunk_path = f"{file_path}_{i // chunk_duration_ms}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def transcribe_audio(file_path):
    """
    Transcribe the audio file at the given path
    """
    model = load_model("base")

    try:
        transcription_result = transcribe(model, file_path, language='en')
        return transcription_result['text']
    except Exception as e:
        raise Exception(f'Failed to transcribe audio file: ',
                        '{file_path}. Error: {e}')
