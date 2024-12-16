@echo off
setlocal

:: Check if venv directory exists
if not exist venv (
    echo Virtual environment not found. Creating new environment...
    python -m venv venv
    
    :: Check if venv creation was successful
    if errorlevel 1 (
        echo Failed to create virtual environment. Please check if Python is installed correctly.
        pause
        exit /b 1
    )
    
    :: Activate the virtual environment
    call venv\Scripts\activate
    
    :: Check if requirements.txt exists
    if exist requirements.txt (
        echo Installing requirements...
        pip install -r requirements.txt
        
        if errorlevel 1 (
            echo Failed to install requirements.
            pause
            exit /b 1
        )
    ) else (
        echo Warning: requirements.txt not found. Skipping package installation.
    )
) else (
    echo Virtual environment found. Activating...
    call venv\Scripts\activate
)

:: Run FastAPI application
echo Starting FastAPI application...
fastapi run .\main.py

:: Deactivate virtual environment on exit
deactivate
endlocal