from django.shortcuts import render, redirect, get_object_or_404
from .forms import AudioFileForm
from .models import AudioFile
from .tasks import transcribe_audio_task

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
                # Trigger the asynchronous transcription task
                print(f'starting async task')
                transcribe_audio_task.delay(file_url, audio_file.pk)
                print(f'redirecting')
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
