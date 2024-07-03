#!/bin/bash

# 스크립트 실행 중 오류 발생 시 즉시 중단
set -e

# 스크립트의 디렉토리를 기준으로 프로젝트 루트 디렉토리 경로 설정
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"


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