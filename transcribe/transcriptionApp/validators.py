from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
import mimetypes
import os


@deconstructible
class AudioFileValidator:
    """
    Validator to check if the uploaded file is a valid audio format and does not exceed the size limit
    """

    valid_mime_types = [
        'audio/mpeg',
        'audio/mpga',
        'audio/wav',
        'audio/webm',
        'audio/mp4',
        'audio/m4a',
    ]

    valid_extensions = [
        '.mp3',
        '.mp4',
        '.m4a',
        '.wav',
        '.webm',
        '.mpeg',
        '.mpga',
    ]

    max_size_mb = 25

    def __call__(self, value):
        # Check MIME type
        mime_type, encoding = mimetypes.guess_type(value.name)
        if mime_type not in self.valid_mime_types:
            raise ValidationError(f'Unsupported file type: {mime_type}.')

        # Check file extension
        if not any(value.name.endswith(ext) for ext in self.valid_extensions):
            raise ValidationError(f'Unsupported file extension. Allowed extensions are: ',
                                  {", ".join(self.valid_extensions)})

        # Check file size
        if value.size > self.max_size_mb * 1024 * 1024:
            raise ValidationError(f'File size exceeds the limit of ',
                                  '{self.max_size_mb}MB.')
