import json
import asyncio
from whisper import load_model
from .models import Transcription, Session
from .tasks import transcribe_audio_chunk
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_name = f"session_{
            self.scope['url_route']['kwargs']['session_name']}"

        await self.channel_layer.group_add(
            self.session_name,
            self.channel_name
        )
        await self.accept()

        self.session = f"{
            self.scope['url_route']['kwargs']['session_name']}"

        self.model = load_model('base')
        self.previous_transcription = ""

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.session_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if bytes_data:
            result = transcribe_audio_chunk.delay(
                bytes_data, self.previous_transcription, self.session)
            transcription = await self.wait_for_result(result)
            self.previous_transcription += transcription + " "

            await self.save_transcription(transcription)

            await self.send(text_data=json.dumps({
                'transcription': transcription
            }))

    async def wait_for_result(self, result):
        """
        Wait for the Celery task to complete and return the result"""
        while not result.ready():
            await asyncio.sleep(1)
        return result.get()

    @database_sync_to_async
    def save_transcription(self, transcription_text):
        """
        Save the transcription to the Transcription model.
        """
        get_session = Session.objects.get(session_name=self.session)

        get_transcription, created = Transcription.objects.get_or_create(
            session=get_session)

        if created:
            get_transcription.transcription = transcription_text
        else:
            get_transcription.transcription += " " + transcription_text

        get_transcription.save()
