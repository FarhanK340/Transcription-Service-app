import os
import requests
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AudioFileForm
from .models import AudioFile
from whisper import load_model, transcribe
from pydub import AudioSegment


# Initialize the transcription model
model = load_model('base')


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
        for chunk in response.iter_content(chunk_size=4 * 1024):
            temp_file.write(chunk)
        temp_file_path = temp_file.name
        return temp_file_path


def transcribe_audio(file_path):
    """
    Transcribe the audio file at the given path
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f'File not found at {file_path}')

    try:
        transcription_result = transcribe(
            model, file_path, language='en')
        return transcription_result['text']
    except Exception as e:
        raise Exception(f'Failed to transcribe audio file: ',
                        '{file_path}. Error: {e}')


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


def upload_audio(request):
    """
    Handle the upload of audio files, transcription, and saving to the database.
    """
    if request.method == "POST":
        form = AudioFileForm(request.POST, request.FILES)

        if form.is_valid():
            audio_file = form.save()
            file_url = audio_file.audio.url

            try:
                file_path = download_tempfile_from_url(file_url)

                if os.path.getsize(file_path) > 25 * 1024 * 1024:
                    # Split large files into chunks
                    chunks = split_large_audio(file_path)
                    transcription_texts = [transcribe_audio(chunk) for chunk in chunks]
                    audio_file.transcription = " ".join(transcription_texts)
                else:
                    audio_file.transcription = transcribe_audio(file_path)

                audio_file.save()
                os.remove(file_path)

                return redirect('transcription', pk=audio_file.pk)
            except Exception as e:
                form.add_error(None, str(e))
    else:
        form = AudioFileForm()

    return render(request, 'transcriptionApp/upload.html', {'form': form})


def view_transcription(request, pk):
    """
    View the transcription of an uploaded audio file
    """
    audio_file = get_object_or_404(AudioFile, pk=pk)
    return render(request, 'transcriptionApp/transcription.html', {'audio_file': audio_file})
