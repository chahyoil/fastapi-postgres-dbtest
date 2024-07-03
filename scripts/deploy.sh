#!/bin/bash

# 데이터베이스가 준비될 때까지 대기
while ! nc -z db 5432; do
  echo "Waiting for postgres..."
  sleep 1
done

echo "PostgreSQL started"

# 마이그레이션 디렉토리가 비어있는지 확인
if [ -z "$(ls -A /dbtest/alembic/versions)" ]; then
  echo "Generating initial migration"
  alembic revision --autogenerate -m "Initial migration"
fi

# 마이그레이션 실행
alembic upgrade head

# FastAPI 애플리케이션 실행
uvicorn app.main:app --host 0.0.0.0 --port 8000