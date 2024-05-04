SUCCESSFUL_RESPONSE = {
    "description": "Successful Response",
    "content": {
        "application/json": {
            "example": {
                "filename": "example.mp3",
                "detected_language": "en",
                "language_probability": 0.9,
                "text": "This is an example transcription.",
                "segments": [
                    {
                        "text": "This is an example",
                        "start": 0.0,
                        "end": 1.5,
                        "words": [
                            {
                                "word": "This",
                                "start": 0.0,
                                "end": 0.2
                            },
                            {
                                "word": "is",
                                "start": 0.2,
                                "end": 0.3
                            },
                            {
                                "word": "an",
                                "start": 0.3,
                                "end": 0.5
                            },
                            {
                                "word": "example",
                                "start": 0.5,
                                "end": 1.0
                            }
                        ]
                    },
                    {
                        "text": "transcription.",
                        "start": 1.5,
                        "end": 2.0
                    }
                ]
            }
        }
    }
}

BAD_REQUEST_RESPONSE = {
    "description": "Bad Request",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "message": "Invalid language. Supported languages are: af, am, ar, ...",
                    "type": "HTTPException",
                    "param": "",
                    "code": 400
                }
            }
        }
    }
}

VALIDATION_ERROR_RESPONSE = {
    "description": "Validation Error",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "message": "Field required",
                    "type": "invalid_request_error",
                    "param": "files",
                    "code": 422
                }
            }
        }
    }
}

INTERNAL_SERVER_ERROR_RESPONSE = {
    "description": "Internal Server Error",
    "content": {
        "application/json": {
            "example": {
                "error": {
                    "message": "An unexpected error occurred.",
                    "type": "Exception",
                    "param": "",
                    "code": 500
                }
            }
        }
    }
}