import os
import tempfile
import speech_recognition as sr
from moviepy import VideoFileClip

class MediaService:
    @staticmethod
    def process_video_or_audio(file_path: str) -> str:
        """
        Extracts audio from a video file (if needed) and transcribes it using SpeechRecognition.
        Supports standard video formats (mp4, mov) and audio formats (wav, mp3, etc. if converted).
        """
        recognizer = sr.Recognizer()
        
        # Try to treat as video first and extract audio
        audio_path = file_path
        extracted_audio_path = None
        try:
            # We use moviepy to extract audio from video
            clip = VideoFileClip(file_path)
            if clip.audio is not None:
                # Create a temporary wav file for speech recognition
                fd, extracted_audio_path = tempfile.mkstemp(suffix='.wav')
                os.close(fd)
                clip.audio.write_audiofile(extracted_audio_path, logger=None)
                audio_path = extracted_audio_path
        except Exception as e:
            print(f"MoviePy extraction skipped or failed (might be an audio file): {e}")

        transcription = ""
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = recognizer.record(source)
                # Using Google's free API for simplicity. For full offline, sphinx or whisper would be used here.
                transcription = recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            transcription = "[Audio could not be understood]"
        except sr.RequestError as e:
            transcription = f"[Speech recognition service error: {e}]"
        except Exception as e:
            print(f"Transcription failed: {e}")
            transcription = "[Transcription failed or file format not supported]"
        finally:
            # Cleanup temp file
            if extracted_audio_path and os.path.exists(extracted_audio_path):
                os.remove(extracted_audio_path)

        return transcription

media_service = MediaService()
