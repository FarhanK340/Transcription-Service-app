from django.shortcuts import render, redirect, get_object_or_404
from .models import Session, Transcription
from .forms import SessionForm


def CreateSession(request):
    if request.method == 'POST':
        form = SessionForm(request.POST)
        if form.is_valid():
            session_name = form.cleaned_data['session_name']
            session_name = session_name.replace(' ', '_')
            try:
                Session.objects.get(session_name=session_name)
            except Session.DoesNotExist:
                Session.objects.create(session_name=session_name)
                print(f'New Session Created')
            return redirect('session', session_name=session_name)
    else:
        form = SessionForm()

    return render(
        request,
        'liveTranscription/index.html',
        {"form": form}
    )


def TranscriptionView(request, session_name):
    get_session = Session.objects.get(session_name=session_name)
    transcription = ''
    try:
        get_transcription = get_object_or_404(
            Transcription, session=get_session.pk)
        transcription = get_transcription.transcription
    except Exception:
        pass

    context = {
        'transcription': transcription,
        'session_name': session_name
    }

    return render(request, 'liveTranscription/session.html', context)
