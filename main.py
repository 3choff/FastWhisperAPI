
import concurrent.futures
import asyncio

from faster_whisper import WhisperModel
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, Form, Depends, status
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from typing import List

# Constants
from constants import device, compute_type, security, MAX_THREADS

# Responses
from responses import SUCCESSFUL_RESPONSE, BAD_REQUEST_RESPONSE
from responses import VALIDATION_ERROR_RESPONSE, INTERNAL_SERVER_ERROR_RESPONSE

# Logging configuration
from logging_config import get_logger
logger = get_logger()

app = FastAPI()

# Helper functions
from utils import authenticate_user
from utils import process_file, validate_parameters

# Routes
@app.get("/", response_class=RedirectResponse)
async def redirect_to_docs():
    return "/docs"

@app.get('/info')
def home():
    return HTMLResponse(content=f"""
        <h1>FastWhisperAPI is running on <span style="color: blue;">{device}</span>!</h1>
        <p>Version: <strong>1.0</strong></p>
        <p>Author: <strong>Edoardo Cilia</strong></p>
        <p>License: <strong>Apache License 2.0</strong></p>
        <h2>Endpoints:</h2>
        <ul>
            <li>
                <h3>/v1/transcriptions</h3>
                <p>Method: POST</p>
                <p>Description: API designed to transcribe audio files leveraging the Faster Whisper library and FastAPI framework.</p>
                <h4>Parameters:</h4>
                <ul>
                    <li>files: A list of audio files to transcribe. This is a required parameter.</li>
                    <li>model_size: The size of the model to use for transcription. This is an optional parameter. The options are 'large', 'medium', 'small', 'base', 'tiny'. Default is 'base'.</li>
                    <li>language: This parameter specifies the language of the audio files. It is optional, with accepted values being lowercase ISO language code (e.g., 'en' for English). If not provided, the system will automatically detect the language.</li>
                    <li>initial_prompt: This optional parameter provides an initial prompt to guide the model's transcription process. It can be used to pass a dictionary of the correct spellings of words and to provide context for better understanding speech, thus maintaining a consistent writing style.</li>
                    <li>vad_filter: Whether to apply a voice activity detection filter. This is an optional parameter. Default is False.</li>
                    <li>min_silence_duration_ms: The minimum duration of silence to be considered as a pause. This is an optional parameter. Default is 1000.</li>
                    <li>response_format: The format of the response. This is an optional parameter. The options are 'text', 'json'. Default is 'text'.</li>
                    <li>timestamp_granularities: The granularity of the timestamps. This is an optional parameter. The options are 'segment', 'word'. Default is 'segment'.</li>
                </ul>
                <h4>Example:</h4>
                <ul>
                    <li>files: audio1.wav, audio2.wav</li>
                    <li>model_size: base</li>
                    <li>language: en</li>
                    <li>initial_prompt: RoBERTa, Mixtral, Claude 3, Command R+, LLama 3.</li>
                    <li>vad_filter: False</li>
                    <li>min_silence_duration_ms: 1000</li>
                    <li>response_format: text</li>
                    <li>timestamp_granularities: segment</li>
                </ul>
                <h4>Example curl request:</h4>
                <ul style="list-style-type:none;">
                    <li>curl -X POST "http://localhost:8000/v1/transcriptions" \</li>
                    <li>-H  "accept: application/json" \</li>
                    <li>-H  "Content-Type: multipart/form-data" \</li>
                    <li>-F "files=@audio1.wav;type=audio/wav" \</li>
                    <li>-F "files=@audio2.wav;type=audio/wav" \</li>
                    <li>-F "model_size=base" \</li>
                    <li>-F "language=en" \</li>
                    <li>-F "initial_prompt=RoBERTa, Mixtral, Claude 3, Command R+, LLama 3." \</li>
                    <li>-F "vad_filter=False" \</li>
                    <li>-F "min_silence_duration_ms=1000" \</li>
                    <li>-F "response_format=text" \</li>
                    <li>-F "timestamp_granularities=segment"</li>
                </ul>
            </li>
            <li>
                <h3>/</h3>
                <p>Method: GET</p>
                <p>Description: Redirects to the /docs endpoint.</p>
            </li>
        </ul>
    """)
@app.post('/v1/transcriptions',
          responses={
              200: SUCCESSFUL_RESPONSE,
              400: BAD_REQUEST_RESPONSE,
              422: VALIDATION_ERROR_RESPONSE,
              500: INTERNAL_SERVER_ERROR_RESPONSE,
          }
)
async def transcribe_audio(credentials: HTTPAuthorizationCredentials = Depends(security),
                           files: List[UploadFile] = File(...),
                           model_size: str = Form("base"),
                           language: str = Form(None),
                           initial_prompt: str = Form(None),
                           vad_filter: bool = Form(False),
                           min_silence_duration_ms: int = Form(1000),
                           response_format: str = Form("text"),
                           timestamp_granularities: str = Form("segment")):
    user = authenticate_user(credentials)
    validate_parameters(files, language, model_size, vad_filter, min_silence_duration_ms, response_format, timestamp_granularities)
    word_timestamps = timestamp_granularities == "word"
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        futures = []
        for file in files:
            future = executor.submit(asyncio.run, process_file(file, model, initial_prompt, language, word_timestamps, vad_filter, min_silence_duration_ms))
            futures.append(future)
    
        transcriptions = {}
        for i, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            try:
                result = future.result()
                if len(files) > 1:
                    if response_format == "text":
                        transcriptions[f"File {i}"] = result["text"]
                    else:
                        transcriptions[f"File {i}"] = result
                else:
                    if response_format == "text":
                        transcriptions = result["text"]
                    else:
                        transcriptions = result
            except Exception as e:
                logger.error(f"An error occurred during transcription: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))
    
        logger.info(f"Transcription completed for {len(files)} files")
        return JSONResponse(content=transcriptions)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail,
    )
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    status_code = 500
    error_type = type(exc).__name__
    if isinstance(exc, ValueError) or isinstance(exc, TypeError):
        status_code = 400
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "message": str(exc),
                "type": error_type,
                "param": "",
                "code": status_code
            }
        },
    )
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    details = exc.errors()[0]['msg']
    loc = exc.errors()[0]['loc']  
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "message": details,
                "type": "invalid_request_error",
                "param": loc[-1] if loc else "",
                "code": 422
            }
        },
    )
# Use the following command to run the FastAPI app:
# fastapi run main.py