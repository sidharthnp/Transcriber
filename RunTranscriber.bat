@echo off
title Whisper Transcriber with SwishFormer Environment
echo Activating SwishFormer conda environment...

REM Initialize conda for batch script
call "C:\Users\HP\anaconda3\Scripts\activate.bat"

REM Activate the SwishFormer environment
call conda activate SwishFormer

REM Check if environment activation was successful
if errorlevel 1 (
    echo ERROR: Failed to activate SwishFormer environment!
    echo Make sure the environment exists and conda is properly installed.
    pause
    exit /b 1
)

echo SwishFormer environment activated successfully!
echo.

REM Change to your transcriber directory
cd /d "C:\Users\HP\Desktop\Transcriber"

REM Check if transcriber.py exists
if not exist "transcriber.py" (
    echo ERROR: transcriber.py not found in the Transcriber folder!
    pause
    exit /b 1
)

REM Run transcriber.py with the activated SwishFormer environment
echo Running transcriber.py with SwishFormer environment...
echo.
python transcriber.py

REM Check if the script ran successfully
if errorlevel 1 (
    echo.
    echo An error occurred while running transcriber.py
    echo The error details should be shown above.
) else (
    echo.
    echo Transcriber finished successfully.
)

echo.
echo Press any key to close this window...
pause

REM Deactivate the environment (optional, as the window will close anyway)
call conda deactivate
