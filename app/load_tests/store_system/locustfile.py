from locust import HttpUser, between
from app.load_tests.store_system.scenario0.stores import StoreBehavior

# 상점 생성: 1000개의 상점이 생성될 때까지 새로운 상점을 생성합니다.
# 상점 조회: 생성된 상점 중 무작위로 하나를 선택하여 조회합니다.
# 상점 목록 조회: 모든 상점의 목록을 조회합니다.
# 상점 정보 업데이트: 무작위로 선택된 상점의 정보를 업데이트합니다.
# 상점 삭제: 무작위로 선택된 상점을 삭제합니다.

class StoreSystemUser(HttpUser):
    wait_time = between(1, 3)
    tasks = [StoreBehavior]