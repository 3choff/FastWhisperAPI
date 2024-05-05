# FastWhisperAPI

FastWhisperAPI is a web service built with the FastAPI framework, specifically tailored for the accurate and efficient transcription of audio files using the Faster Whisper library.
This project is an open-source initiative that leverages the remarkable Faster Whisper model. It is four times faster than openai/whisper while maintaining the same level of accuracy and consuming less memory, whether running on CPU or GPU. The API is built to provide compatibility with the OpenAI API standard, facilitating seamless integration into existing applications that use [OpenAI - Whisper](https://platform.openai.com/docs/api-reference/making-requests).

## Features
- FastWhisperAPI is fully compatible with the OpenAI API standard.
- Transcribe audio files asynchronously using a ThreadPoolExecutor.
- Support for submitting multiple files per request.
- Support for multiple languages and model sizes.
- Customizable initial prompt to guide the model's transcription process.
- Voice activity detection filter.
- Customizable response format and timestamp granularities.

## Requirements
- Python 3.8 or greater
- Refer to the Faster Whisper documentation for the GPU requirements [here](https://github.com/SYSTRAN/faster-whisper/blob/master/README.md).

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/3choff/FastWhisperAPI.git
    ```

2. Navigate to the project directory:
    ```bash
    cd FastWhisperAPI
    ```

3. Create a new environment:
    ```bash
    python3 -m venv FastWhisperAPI
    ```

4. Activate the virtual environment:

   - **On Unix/Linux/macOS**:
     ```bash
     source FastWhisperAPI/bin/activate
     ```

   - **On Windows**:
     ```bash
     FastWhisperAPI\Scripts\activate
     ```

5. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```


## Usage

To run the FastAPI app, use the following command:

```bash
fastapi run main.py
```
The application will start running at `http://localhost:8000`.

This API can be dockerized for deployment, but it is also possible to run the API from a Google Colab using the NGROK service. The Jupyter Notebook is included in the repository.

## Parameters

- `files`: A list of audio files to transcribe. This is a required parameter.
- `model_size`: The size of the model to use for transcription. This is an optional parameter. The options are 'large', 'medium', 'small', 'base', 'tiny'. Default is 'base'.
- `language`: This parameter specifies the language of the audio files. It is optional, with accepted values being lowercase ISO language code (e.g., 'en' for English). If not provided, the system will automatically detect the language.
- `initial_prompt`: This optional parameter provides an initial prompt to guide the model's transcription process. It can be used to pass a dictionary of the correct spellings of words and to provide context for better understanding speech, thus maintaining a consistent writing style.
- `vad_filter`: Whether to apply a voice activity detection filter. This is an optional parameter. Default is False.
- `min_silence_duration_ms`: The minimum duration of silence to be considered as a pause. This is an optional parameter. Default is 1000.
- `response_format`: The format of the response. This is an optional parameter. The options are 'text', 'json'. Default is 'text'.
- `timestamp_granularities`: The granularity of the timestamps. This is an optional parameter. The options are 'segment', 'word'. Default is 'segment'.

### Example curl request

You can use the following `curl` command to send a POST request to the `/v1/transcriptions` endpoint:

```bash
curl -X POST "http://localhost:8000/v1/transcriptions" \
-H  "accept: application/json" \
-H  "Content-Type: multipart/form-data" \
-F "files=@audio1.wav;type=audio/wav" \
-F "files=@audio2.wav;type=audio/wav" \
-F "model_size=base" \
-F "language=en" \
-F "initial_prompt=RoBERTa, Mixtral, Claude 3, Command R+, LLama 3." \
-F "vad_filter=False" \
-F "min_silence_duration_ms=1000" \
-F "response_format=text" \
-F "timestamp_granularities=segment"
```
## Endpoints

- `/`: Redirects to the `/docs` endpoint, which provides a Swagger UI for interactive exploration of the API. You can call and test the API directly from your browser.
- `/info`: Provides information about the device used for transcription and the parameters.
- `/v1/transcriptions`: API designed to transcribe audio files.

## Acknowledgements

This project was made possible thanks to:

- [Faster Whisper](https://github.com/SYSTRAN/faster-whisper): For providing the transcription model used in this project.
- [FastAPI](https://github.com/tiangolo/fastapi): For the web framework used to build the API.
- [AI Anytime](https://www.youtube.com/watch?v=NU406wZz1eU): For inspiring this project.

## License

This project is licensed under the Apache License 2.0.
