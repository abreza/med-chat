import os
import tempfile
import base64
from typing import Union, Optional
from .client import ASRServiceClient

asr_client = ASRServiceClient()


def transcribe_file(file_path: str, language: Optional[str] = None, region: Optional[str] = None) -> str:
    if not os.path.exists(file_path):
        print(f"Audio file not found: {file_path}")
        return ""

    try:
        result = asr_client.transcribe_file(file_path, language, region)
        if result:
            transcription = result.get('text', '').strip()
            detected_info = f"Language: {result.get('language', 'unknown')}"
            if result.get('region'):
                detected_info += f", Region: {result.get('region')}"
            
            print(f"Transcribed: '{transcription}' ({detected_info})")
            return transcription
        return ""
        
    except Exception as e:
        print(f"Transcription error for file {file_path}: {e}")
        return ""
    
    finally:
        try:
            if file_path.startswith(tempfile.gettempdir()):
                os.unlink(file_path)
        except Exception as e:
            print(f"Failed to clean up temporary file {file_path}: {e}")


def transcribe_base64(base64_audio: str, language: Optional[str] = None, region: Optional[str] = None) -> str:
    if not base64_audio:
        return ""
        
    try:
        result = asr_client.transcribe_base64(base64_audio, language, region)
        if result:
            transcription = result.get('text', '').strip()
            print(f"Transcribed base64 audio: '{transcription}'")
            return transcription
        return ""
        
    except Exception as e:
        print(f"Base64 transcription error: {e}")
        return ""


def transcribe(audio_input: Union[tuple, bytes, str], 
               language: Optional[str] = None,
               region: Optional[str] = None) -> str:
    if audio_input is None:
        return ""

    try:
        if isinstance(audio_input, str):
            return transcribe_file(audio_input, language, region)
            
        elif isinstance(audio_input, bytes):
            base64_audio = base64.b64encode(audio_input).decode('utf-8')
            return transcribe_base64(base64_audio, language, region)
            
        elif isinstance(audio_input, tuple) and len(audio_input) == 2:
            sample_rate, audio_data = audio_input
            
            import wave
            import numpy as np
            
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            try:
                with wave.open(temp_file.name, 'wb') as wav_file:
                    wav_file.setnchannels(1)
                    wav_file.setsampwidth(2)
                    wav_file.setframerate(sample_rate)
                    
                    if isinstance(audio_data, np.ndarray):
                        if audio_data.dtype != np.int16:
                            if audio_data.dtype in [np.float32, np.float64]:
                                audio_data = (audio_data * 32767).astype(np.int16)
                            else:
                                audio_data = audio_data.astype(np.int16)
                        wav_file.writeframes(audio_data.tobytes())
                    
                temp_file.close()
                return transcribe_file(temp_file.name, language, region)
                
            finally:
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
        else:
            print(f"Unsupported audio input type: {type(audio_input)}")
            return ""
            
    except Exception as e:
        print(f"Transcription error: {e}")
        return ""
