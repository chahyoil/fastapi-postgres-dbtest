# 기본 이미지로 Python 3.12 slim 버전 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 설치
RUN pip install --no-cache-dir poetry

# 프로젝트 파일 복사
COPY pyproject.toml poetry.lock ./
COPY app ./app

# Poetry를 사용하여 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# 애플리케이션 실행
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]