import os
import tempfile
from fastapi import Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPAuthorizationCredentials
from faster_whisper import WhisperModel
from constants import security, SUPPORTED_EXTENSIONS, SUPPORTED_LANGUAGES, SUPPORTED_MODELS, SUPPORTED_RESPONSE_FORMATS, SUPPORTED_TIMESTAMP_GRANULARITIES
from logging_config import get_logger

logger = get_logger()
def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    correct_api_key = "dummy_api_key"  # replace with your dummy API key
    if credentials.scheme != "Bearer" or credentials.credentials != correct_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "message": "Incorrect API key",
                    "type": "invalid_request_error",
                    "param": "Authorization",
                    "code": 401
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials
def get_file_extension(filename: str) -> str:
    _, extension = os.path.splitext(filename)
    return extension[1:].lower()
async def transcribe_temp_file(file: UploadFile, extension: str, model: WhisperModel, initial_prompt: str, language: str, word_timestamps: bool, vad_filter: bool, min_silence_duration_ms: int):
    temp_file = tempfile.NamedTemporaryFile(suffix=extension, delete=False)
    try:
        temp_file.write(await file.read())
        temp_file.close()
        vad_parameters = dict(min_silence_duration_ms=min_silence_duration_ms) if vad_filter else None
        segments, info = model.transcribe(temp_file.name, initial_prompt=initial_prompt, language=language, beam_size=5, vad_filter=vad_filter, vad_parameters=vad_parameters, word_timestamps=word_timestamps)
    finally:
        os.unlink(temp_file.name)
    return segments, info

def create_segment_data(segments: list, word_timestamps: bool):
    segment_data = []
    for segment in segments:
        segment_dict = {
            "text": segment.text.strip(),
            "start": segment.start,
            "end": segment.end,
        }
        if word_timestamps:
            words_data = []
            for word in segment.words:
                words_data.append({
                    "word": word.word.strip(),
                    "start": word.start,
                    "end": word.end
                })
            segment_dict["words"] = words_data
        segment_data.append(segment_dict)
    return segment_data
async def process_file(file: UploadFile, model: WhisperModel, initial_prompt: str, language: str, word_timestamps: bool, vad_filter: bool,  min_silence_duration_ms: int):
    extension = get_file_extension(file.filename)
    segments, info = await transcribe_temp_file(file, extension, model, initial_prompt, language, word_timestamps, vad_filter, min_silence_duration_ms)
    segment_data = create_segment_data(segments, word_timestamps)
    full_text = " ".join([segment["text"] for segment in segment_data]).strip()
    return {
        "filename": file.filename,
        "detected_language": info.language,
        "language_probability": info.language_probability,
        "text": full_text,
        "segments": segment_data
    }

def validate_parameters(files, language, model_size, vad_filter, min_silence_duration_ms, response_format, timestamp_granularities):
    for file in files:
        extension = get_file_extension(file.filename)
        if extension not in SUPPORTED_EXTENSIONS:
            logger.warning(f"Invalid file extension: {extension}")
            raise HTTPException(status_code=400, detail={
                "error": {
                    "message": f"Invalid file extension. Supported extensions are: {', '.join(SUPPORTED_EXTENSIONS)}",
                    "type": "invalid_request_error",
                    "param": "files",
                    "code": 400
                }
            })
    if language is not None and language not in SUPPORTED_LANGUAGES:
        logger.warning(f"Invalid language: {language}")
        raise HTTPException(status_code=400, detail={
            "error": {
                "message": f"Invalid language {language}. Language parameter must be specified in ISO-639-1 format.",
                "type": "invalid_request_error",
                "param": "language",
                "code": 400
            }
        })
    if model_size not in SUPPORTED_MODELS:
        logger.warning(f"Invalid model size: {model_size}")
        raise HTTPException(status_code=400, detail={
            "error": {
                "message": f"Invalid model size. Supported models are: {', '.join(SUPPORTED_MODELS)}",
                "type": "invalid_request_error",
                "param": "model",
                "code": 400
            }
        })
    if not isinstance(vad_filter, bool):
        logger.warning(f"Invalid vad_filter value: {vad_filter}")
        raise HTTPException(status_code=400, detail={
            "error": {
                "message": "Invalid vad_filter value. It should be a boolean.",
                "type": "invalid_request_error",
                "param": "vad_filter",
                "code": 400
            }
        })
    if not isinstance(min_silence_duration_ms, int) or min_silence_duration_ms < 0:
        logger.warning(f"Invalid min_silence_duration_ms value: {min_silence_duration_ms}")
        raise HTTPException(status_code=400, detail={
            "error": {
                "message": "Invalid min_silence_duration_ms value. It should be a non-negative integer.",
                "type": "invalid_request_error",
                "param": "min_silence_duration_ms",
                "code": 400
            }
        })
    if response_format not in SUPPORTED_RESPONSE_FORMATS:
        logger.warning(f"Invalid response_format value: {response_format}")
        raise HTTPException(status_code=400, detail={
            "error": {
                "message": f"Invalid response_format. Supported format are: {', '.join(SUPPORTED_RESPONSE_FORMATS)}",
                "type": "invalid_request_error",
                "param": "response_format",
                "code": 400
            }
        })
    if timestamp_granularities not in SUPPORTED_TIMESTAMP_GRANULARITIES:
        logger.warning(f"Invalid timestamp_granularities value: {timestamp_granularities}")
        raise HTTPException(status_code=400, detail={
            "error": {
                "message": f"Invalid timestamp_granularities. Supported format are: {', '.join(SUPPORTED_TIMESTAMP_GRANULARITIES)}",
                "type": "invalid_request_error",
                "param": "timestamp_granularities",
                "code": 400
            }
        })