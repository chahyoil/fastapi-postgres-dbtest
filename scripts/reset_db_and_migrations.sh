#!/bin/bash

# 스크립트 실행 중 오류 발생 시 즉시 중단
set -e

# 스크립트의 디렉토리를 기준으로 프로젝트 루트 디렉토리 경로 설정
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "데이터베이스 및 마이그레이션 재설정을 시작합니다..."

# 프로젝트 루트 디렉토리로 이동
cd "$PROJECT_ROOT"

# 1. Docker 컨테이너와 볼륨 중지 및 제거
echo "Docker 컨테이너와 볼륨을 제거합니다..."
docker-compose down -v

# 2. Docker 컨테이너 다시 시작
echo "Docker 컨테이너를 다시 시작합니다..."
docker-compose up -d

# 잠시 대기하여 데이터베이스가 완전히 시작되도록 함
echo "데이터베이스가 시작되기를 기다립니다..."
sleep 10

# 3. alembic_version 테이블 비우기 (존재한다면)
echo "alembic_version 테이블을 비웁니다..."
docker-compose exec db psql -U user -d testdb -c "DELETE FROM alembic_version;" || true

# 4. 새로운 마이그레이션 생성
echo "새로운 마이그레이션을 생성합니다..."
docker-compose exec app alembic revision --autogenerate -m "recreate initial migration"

# 5. 마이그레이션 적용
echo "마이그레이션을 적용합니다..."
docker-compose exec app alembic upgrade head

# 6. 마이그레이션 상태 확인
echo "마이그레이션 상태를 확인합니다..."
docker-compose exec app alembic history
docker-compose exec app alembic current

# 7. 애플리케이션 재시작
echo "애플리케이션을 재시작합니다..."
docker-compose restart app

echo "데이터베이스 및 마이그레이션 재설정이 완료되었습니다."