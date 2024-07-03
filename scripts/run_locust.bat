@echo off
setlocal

REM 기본값 설정
set SYSTEM=%1
if "%SYSTEM%"=="" set SYSTEM=store_system

set LOCUST_FILE=%2
if "%LOCUST_FILE%"=="" set LOCUST_FILE=locustfile.py

set HOST=%3
if "%HOST%"=="" set HOST=http://localhost:8000

REM Locust 실행
docker-compose exec app locust -f /dbtest/app/load_tests/%SYSTEM%/%LOCUST_FILE% --host %HOST%

endlocal