# 기본 이미지로 Python 3.11 slim 버전 사용
FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /dbtest

# 필요한 패키지 설치
RUN apt-get update && apt-get install -y netcat-openbsd vim && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install --no-cache-dir poetry

# 프로젝트 파일 복사
COPY pyproject.toml poetry.lock ./
COPY app ./app
COPY pytest.ini ./
COPY .env ./

# Poetry를 사용하여 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

COPY alembic.ini .
COPY alembic ./alembic
COPY scripts/deploy.sh .
RUN chmod +x deploy.sh

CMD ["./deploy.sh"]