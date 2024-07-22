import boto3, tempfile, os
from django.conf import settings
from django.shortcuts import render, redirect
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import AudioFileForm
from .models import AudioFile
from whisper import load_model, transcribe

# Create your views here.

model = load_model('base')


def home(request):
    return render(request, 'home.html')

def download_file_from_s3(bucket_name, s3_key):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        s3_client.download_fileobj(bucket_name, s3_key, temp_file)
        temp_file_path = temp_file.name
    return temp_file_path

def upload_audio(request):
    if request.method == "POST":
        form = AudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = form.save()

            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            try:
                s3_key = f'audio/{request.FILES["audio"].name}'
                s3_client.upload_fileobj(
                    request.FILES['audio'],
                    settings.AWS_STORAGE_BUCKET_NAME,
                    s3_key
                )
            except NoCredentialsError:
                return render(request, 'transcriptionApp/upload.html', {'form': form, 'error': 'Credentials not available'})
            except PartialCredentialsError:
                return render(request, 'transcriptionApp/upload.html', {'form': form, 'error': 'Incomplete credentials'})
            except Exception as e:
                return render(request, 'transcriptionApp/upload.html', {'form': form, 'error': str(e)})

            try:
                temp_file_path = download_file_from_s3(settings.AWS_STORAGE_BUCKET_NAME, s3_key)
                
                transcription_result = transcribe(model, temp_file_path) 
                audio_file.transcription = transcription_result['text']
                audio_file.save()
                
                os.remove(temp_file_path)

            except Exception as e:
                return render(request, 'transcriptionApp/upload.html', {'form': form, 'error': str(e)})

            return redirect('transcription', pk=audio_file.pk)
    else:
        form = AudioFileForm()
    
    return render(request, 'transcriptionApp/upload.html', {'form': form})

def view_transcription(request, pk):
    audio_file = AudioFile.objects.get(pk=pk)
    return render(request, 'transcriptionApp/transcription.html', {'audio_file': audio_file})
