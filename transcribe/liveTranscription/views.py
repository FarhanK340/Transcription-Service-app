from .forms import SessionForm
from .models import Session, Transcription
from django.shortcuts import render, redirect, get_object_or_404


def CreateSession(request):
    """
    Handle the creation or retrieval of a session 
    """
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session_name = form.cleaned_data['session_name']
            session_name = session_name.replace(' ', '_')
            Session.objects.get_or_create(session_name=session_name)
            return redirect('session', session_name=session_name)
    else:
        form = SessionForm()

    return render(
        request,
        'liveTranscription/index.html',
        {"form": form}
    )


def TranscriptionView(request, session_name):
    """
    Display the transcription for a given session
    """
    try:
        # Retrieve the session object
        get_session = get_object_or_404(Session, session_name=session_name)
        
        # Retrieve the transcription object
        get_transcription = get_object_or_404(Transcription, session=get_session.pk)
        transcription = get_transcription.transcription

    except Exception as e:
        # Log the error or handle it as needed
        print(f'Error encountered: {e}')
        transcription = 'An error occurred while retrieving the transcription.'

    context = {
        'transcription': transcription,
        'session_name': session_name
    }

    return render(request, 'liveTranscription/session.html', context)
