# 1. Python bazaviy imij
FROM python:3.10-slim

# 2. Ishchi katalog
WORKDIR /app

# 3. Loyihani konteynerga ko‘chirish
COPY . /app

# 4. Kerakli kutubxonalarni o‘rnatish
RUN pip install --no-cache-dir -r requirements.txt

# 5. PORT (Cloupard avtomatik o‘rnatadi)
ENV PORT=5000

# 6. Flaskni ishga tushirish
CMD ["python", "app.py"]
