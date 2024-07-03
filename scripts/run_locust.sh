#!/bin/bash

# 기본값 설정
SYSTEM=${1:-store_system}
LOCUST_FILE=${2:-locustfile.py}
HOST=${3:-http://localhost:8000}

# Locust 실행
docker-compose exec app locust -f /dbtest/app/load_tests/${SYSTEM}/${LOCUST_FILE} --host ${HOST}