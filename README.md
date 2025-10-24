# UTS Sistem Terdistribusi — Pub-Sub Log Aggregator

Proyek ini mengimplementasikan Publish–Subscribe Event Aggregator menggunakan FastAPI + asyncio, dengan fokus pada idempotent consumer, deduplication, dan persistensi event.
Seluruh komponen berjalan di dalam Docker container, serta mendukung eksekusi lokal tanpa Docker.

## Fitur

- **Publish / Subscribe Pattern**
  - Endpoint `POST /publish` menerima satu atau beberapa event dalam format JSON.
  - Worker async memproses event di background menggunakan `asyncio.Queue`.

- **Deduplication & Idempotency**
  - Event dikenali secara unik oleh `(topic, event_id)`.
  - Duplikat tidak akan diproses ulang, bahkan setelah restart container (persisten di SQLite).

- **Monitoring & Statistik**
  - `GET /events?topic=...` → menampilkan event unik per topik.  
  - `GET /stats` → menampilkan metrik sistem, seperti:
    - total event diterima  
    - jumlah event unik diproses  
    - duplikasi yang di-drop  
    - daftar topik aktif  
    - uptime aplikasi  

---

## teknologi yang dipakai

| Komponen | Teknologi |
|----------|------------|
| Bahasa Pemrograman | Python 3.11 |
| Framework | FastAPI |
| Database | SQLite |
| Runtime | AsyncIO |
| Container | Docker + Docker Compose |

Dependensi tambahan dapat dilihat di **requirements.txt**.

---

## Menjalankan dengan Docker Compose

1. Clone repository
   ```bash
   git clone https://github.com/<username>/uts-aggregator.git
   cd uts-aggregator
   ```
2. Build dan jalankan container
   ```bash
   docker compose build --no-cache
   docker compose up -d aggregator
   docker compose run --rm publisher python -m src.publisher
   ```
3. Periksa statistik
   ```bash
   curl http://localhost:8080/stats
   ```

### Konfigurasi
- `AGGREGATOR_URL` (default `http://aggregator:8080/publish`)
- (Disarankan) `DEDUP_DB_PATH` agar mudah dikontrol saat testing, default `data/dedup.db`

## Struktur Repo (ringkas)
```
src/
  main.py           # FastAPI app + workers + endpoints
  consumer.py       # worker logic (idempotent)
  publisher.py      # generator + pengirim batch (>=20% dup)
  dedup_store.py    # SQLite-based durable dedup store
tests/
  test_app.py
  test_persist_and_stress.py   # (ditambahkan)
Dockerfile
docker-compose.yml
requirements.txt
README.md
report.md
```

## Unit Test
Jalankan:
```bash
pytest -v
```

Cakupan utama:
- Validasi skema (422 jika salah)
- Idempotency (duplikat tidak diproses)
- Persistensi dedup (tetap efektif setelah restart)
- Konsistensi `/stats` dan `/events`
- **Stress mini** ≥5000 event dengan ≥20% duplikat

## Demo Cepat (PowerShell)
```powershell
Write-Host "=== Sebelum ==="
(Invoke-RestMethod -Uri "http://localhost:8080/stats") | ConvertTo-Json -Depth 5

docker compose run --rm publisher python -m src.publisher

Write-Host "=== Sesudah ==="
(Invoke-RestMethod -Uri "http://localhost:8080/stats") | ConvertTo-Json -Depth 5
```

## Catatan Desain
- *At-least-once delivery* di publisher dengan duplikasi terkontrol
- Consumer idempotent via kunci `(topic,event_id)`
- Dedup store **SQLite** pada named volume (`appdata:/app/data`)
- Ordering **best-effort per-topic** (timestamp) — tidak memaksakan total ordering

## Link demo

