import boto3
from django.conf import settings
from django.shortcuts import render, redirect
from .forms import AudioFileForm
from .models import AudioFile
from whisper import load_model, transcribe


model = load_model('base')


def upload_audio(request):
    if request.method == "POST":
        form = AudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = form.save(commit=False)
            file_obj = request.FILES['audio']

            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            s3_key = f'audio/{file_obj.name}'
            try:
                s3_client.upload_fileobj(
                    file_obj, settings.AWS_STORAGE_BUCKET_NAME, s3_key)

                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                            'Key': s3_key},
                    ExpiresIn=3600
                )

                transcription_result = transcribe(model, presigned_url)
                audio_file.transcription = transcription_result['text']
                audio_file.save()

            except Exception as e:
                return render(request, 'transcriptionApp/upload.html', {'form': form, 'error': str(e)})

            return redirect('transcription', pk=audio_file.pk)
    else:
        form = AudioFileForm()

    return render(request, 'transcriptionApp/upload.html', {'form': AudioFileForm()})


def view_transcription(request, pk):
    audio_file = AudioFile.objects.get(pk=pk)
    return render(request, 'transcriptionApp/transcription.html', {'audio_file': audio_file})
