import os
import boto3
import requests
import tempfile
from django.shortcuts import render, redirect, get_object_or_404
from .forms import AudioFileForm
from .models import AudioFile
from whisper import load_model, transcribe


model = load_model('base')


def download_file_from_url(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            for chunk in response.iter_content(chunk_size=4 * 1024):
                temp_file.write(chunk)
            temp_file_path = temp_file.name
            return temp_file_path
    else:
        raise Exception("Failed to download file from URL: {url}")


def upload_audio(request):
    if request.method == "POST":
        form = AudioFileForm(request.POST, request.FILES)

        if form.is_valid():
            audio_file = form.save()
            file_url = audio_file.audio.url

            file_path = download_file_from_url(file_url)

            if os.path.exists(file_path):
                transcription_result = transcribe(
                    model, file_path, language='en')
                audio_file.transcription = transcription_result['text']
                audio_file.save()

                os.remove(file_path)
            else:
                raise FileNotFoundError(f'File not found at {file_path}')

            return redirect('transcription', pk=audio_file.pk)
    else:
        form = AudioFileForm()

    return render(request, 'transcriptionApp/upload.html', {'form': AudioFileForm()})


def view_transcription(request, pk):
    audio_file = get_object_or_404(AudioFile, pk=pk)
    return render(request, 'transcriptionApp/transcription.html', {'audio_file': audio_file})
