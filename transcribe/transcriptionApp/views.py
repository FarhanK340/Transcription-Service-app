import os
import boto3
import requests
import tempfile
from django.conf import settings
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
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
            audio_file = form.save(commit=False)
            file_obj = request.FILES['audio']
            title = form.cleaned_data['title']

            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            s3_key = f'audio/{title}_{file_obj.name}'
            try:
                s3_client.upload_fileobj(
                    file_obj, settings.AWS_STORAGE_BUCKET_NAME, s3_key)

                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                            'Key': s3_key},
                    ExpiresIn=1800
                )

                file_path = download_file_from_url(presigned_url)
           
                if os.path.exists(file_path):
                    transcription_result = transcribe(model, file_path, language='en')
                    audio_file.transcription = transcription_result['text']

                    with open(file_path, 'rb') as f:
                        audio_content = f.read()
                        audio_file.audio.save(f"{title}_{file_obj.name}", ContentFile(audio_content), save=False)
                    
                    audio_file.save()


                    os.remove(file_path)
                else:
                    raise FileNotFoundError(f'File not found at {file_path}')

            except Exception as e:
                return render(request, 'transcriptionApp/upload.html', {'form': form, 'error': str(e)})
           
    
            return redirect('transcription', pk=audio_file.pk)
    else:
        form = AudioFileForm()

    return render(request, 'transcriptionApp/upload.html', {'form': AudioFileForm()})


def view_transcription(request, pk):
    audio_file = get_object_or_404(AudioFile, pk = pk)
    return render(request, 'transcriptionApp/transcription.html', {'audio_file': audio_file})
