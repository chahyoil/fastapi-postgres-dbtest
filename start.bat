@echo off
SET MODE=%1

IF "%MODE%"=="dev" (
    echo Starting in development mode...
    poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
) ELSE IF "%MODE%"=="prod" (
    echo Starting in production mode...
    poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
) ELSE (
    echo Invalid mode specified. Use "dev" or "prod".
)

pause