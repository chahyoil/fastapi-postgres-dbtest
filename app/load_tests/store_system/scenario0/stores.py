import random
from locust import task, TaskSet
from app.store_system.tests.factories import StoreFactory

class StoreBehavior(TaskSet):
    def on_start(self):
        self.store_ids = []

    @task(1)
    def create_store(self):
        if len(self.store_ids) >= 1000:
            return

        store_data = StoreFactory.to_dict(StoreFactory.build())
        response = self.client.post("/store-system/stores/", json=store_data)
        if response.status_code == 200:
            store_id = response.json()["id"]
            self.store_ids.append(store_id)

    @task(5)
    def read_store(self):
        if not self.store_ids:
            return

        store_id = random.choice(self.store_ids)
        self.client.get(f"/store-system/stores/{store_id}")

    @task(3)
    def read_stores(self):
        self.client.get("/store-system/stores/")

    @task(2)
    def update_store(self):
        if not self.store_ids:
            return

        store_id = random.choice(self.store_ids)
        store_data = StoreFactory.to_dict(StoreFactory.build())
        self.client.put(f"/store-system/stores/{store_id}", json=store_data)

    @task(1)
    def delete_store(self):
        if not self.store_ids:
            return

        store_id = random.choice(self.store_ids)
        response = self.client.delete(f"/store-system/stores/{store_id}")
        if response.status_code == 200:
            self.store_ids.remove(store_id)