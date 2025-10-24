FROM python:3.11-slim

# 1) Buat user non-root
RUN useradd -m -u 1000 appuser

# 2) Siapkan direktori kerja
RUN install -d -o appuser -g appuser /app

WORKDIR /app

# 3) Install deps dulu biar cache efisien
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4) Salin kode dengan owner appuser (TANPA inline comment)
COPY --chown=appuser:appuser . .

# 5) Pastikan folder data ada & milik appuser (kalau tidak ikut di .dockerignore)
RUN install -d -o appuser -g appuser /app/data

# 6) Jalan sebagai non-root
USER appuser

# (CMD bisa di-compose)
# CMD ["python", "-m", "src.main"]
