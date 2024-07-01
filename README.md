# 파이썬과 postgreSQL 로 db 연습 및 테스트 목적 레퍼지토리

## 프로젝트 개요 

- FastAPI를 사용하여 PostgreSQL 데이터베이스의 성능을 테스트하기 위한 목적으로 구성함
- 병원 시스템, 주차 시스템, 상점 시스템 등 다양한 시나리오를 구현하여 데이터베이스 성능을 측정하고 분석
- ORM 설정 및 relation 을 다양하게 해서 연관관계 설정을 연습

## 구성요소

- Python 3.12
- PostgreSQL 13
- FastAPI 0.78.0
- SQLAlchemy 1.4.36
- Grafana 8.2
- Prometheus 2.30.3
- Docker 및 Docker Compose

## 패키지 매니저 

- poetry

## 프로젝트 구성 

* app : 
    * core 
    * hospital_system
    * load_tests
    * parking_system
    * store_system
* grafana
* logs
* prometheus

## 주요 기능 [TODO_LIST]

- FastAPI를 이용한 RESTful API 구현
- SQLAlchemy를 통한 데이터베이스 ORM
- Prometheus를 이용한 메트릭 수집
- Grafana를 통한 데이터 시각화 
- Locust를 이용한 부하 테스트
- pytest를 이용한 단위 및 통합 테스트

## 설치 및 실행

1. 저장소 클론:
```
git clone https://github.com/chahyoil/fastapi-postgres-dbtest
```
2. 프로젝트 디렉토리로 이동
```
cd fastapi-postgres-dbtest
```
3. Poetry를 이용한 의존성 설치:
```
poetry install
```
4. 환경 변수 설정:
- .env 파일을 생성하고 필요한 환경 변수를 설정합니다.

5. Docker Compose를 이용한 서비스 실행:
```
docker-compose up -d
```
6. 개발 서버 실행:
```
poetry run start-dev
```

## API 문서

## 테스트

## 모니터링

- Prometheus : http://localhost:9090
- Grafana : http://localhost:3000

