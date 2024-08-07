import json
from .tasks import transcribe_audio_chunk
from .models import Transcription, Session
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class AudioConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when the WebSocket connection is established.
        Adds the consumer to the session group.
        """
        self.session = f"{
            self.scope['url_route']['kwargs']['session_name']}"

        await self.channel_layer.group_add(
            self.session,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self):
        """
        Called when the WebSocket connection is closed.
        Removes the consumer from the session group.
        """
        await self.channel_layer.group_discard(
            self.session,
            self.channel_name
        )

    async def receive(self, bytes_data=None):
        """
        Called when a message is received from the WebSocket.
        Processes the audio data by sending it for transcription.
        """
        if bytes_data:
            # Send the aaudio data for asynchronous transcription
            result = transcribe_audio_chunk.delay(
                bytes_data, self.session)
            transcription = result.get()

            # Save the transcription to the database
            await self.save_transcription(transcription)

            # Send the transcription result back to the WebSocket client
            await self.send(text_data=json.dumps({
                'transcription': transcription
            }))

    @database_sync_to_async
    def save_transcription(self, transcription_text):
        """
        Save the transcription to the Transcription model.

        Args:
            transcription_text (str): The transcribed text to be saved.
        """
        get_session = Session.objects.get(session_name=self.session)
        get_transcription, created = Transcription.objects.get_or_create(
            session=get_session)
        get_transcription.transcription = transcription_text

        get_transcription.save()
