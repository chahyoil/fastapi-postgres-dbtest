#!/bin/bash

MODE=$1

if [ "$MODE" == "dev" ]; then
    echo "Starting in development mode..."
    poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
elif [ "$MODE" == "prod" ]; then
    echo "Starting in production mode..."
    poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    echo "Invalid mode specified. Use 'dev' or 'prod'."
fi