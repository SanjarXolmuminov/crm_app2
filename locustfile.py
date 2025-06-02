from locust import HttpUser, task, between

class CRMUser(HttpUser):
    wait_time = between(1, 5)  # Har bir so‘rov orasida 1-5 soniya kutadi

    @task
    def view_customers(self):
        self.client.get("/login")  # Mijozlar ro‘yxati sahifasi

    @task
    def view_products(self):
        self.client.get("/products")  # Mahsulotlar sahifasi

    @task
    def view_sell(self):
        self.client.get("/sell")  # Sotish sahifasi
