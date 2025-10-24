# src/publisher.py
import httpx
import uuid
import random
import asyncio
import os
from datetime import datetime
import json

AGG_URL = os.getenv("AGGREGATOR_URL", "http://aggregator:8080/publish")
TOTAL = 5000
BATCH = 100
DUP_RATE = 0.20  # 20% duplicates

async def send_batches(events_batches):
    async with httpx.AsyncClient(timeout=60.0) as client:
        for idx, batch in enumerate(events_batches, start=1):
            try:
                resp = await client.post(AGG_URL, json=batch)
                if resp.status_code != 200:
                    print(f"[ERROR {resp.status_code}] Batch {idx}: {resp.text}")
                else:
                    print(f"[OK] Batch {idx}/{len(events_batches)} sent.")
            except Exception as e:
                print(f"[EXCEPTION] Batch {idx}: {e}")
            await asyncio.sleep(0.02)  

def make_events():
    events = []
    for i in range(TOTAL):
        event_id = str(uuid.uuid4())
        ev = {
            "topic": f"topic-{random.randint(1,10)}",
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "source": "publisher-service",
            "payload": {"seq": i, "value": random.uniform(20, 35)}
        }
        events.append(ev)

    num_duplicates = int(TOTAL * DUP_RATE)
    duplicates = random.sample(events, num_duplicates)
    events += duplicates
    random.shuffle(events)

    batches = [events[i:i+BATCH] for i in range(0, len(events), BATCH)]
    return batches

async def main():
    batches = make_events()
    print(f"Total batch: {len(batches)} ({TOTAL} events, {int(TOTAL * DUP_RATE)} duplicates)")

    async with httpx.AsyncClient(timeout=60.0) as client:
        # kirim semua batch
        for idx, batch in enumerate(batches, start=1):
            try:
                resp = await client.post(AGG_URL, json=batch)
                if resp.status_code != 200:
                    print(f"[ERROR {resp.status_code}] Batch {idx}: {resp.text}")
                else:
                    print(f"[OK] Batch {idx}/{len(batches)} sent.")
            except Exception as e:
                print(f"[EXCEPTION] Batch {idx}: {e}")
            await asyncio.sleep(0.02)

        print("✅ Done sending all events.")

        # ambil statistik setelah semua batch terkirim
        try:
            stats_url = os.getenv("AGGREGATOR_STATS_URL", AGG_URL.replace("/publish", "/stats"))
            stats = await client.get(stats_url)
            if stats.status_code == 200:
                print("\n📊 Aggregator Stats:")
                print(json.dumps(stats.json(), indent=2))
            else:
                print(f"[WARN] Gagal ambil stats: {stats.status_code} - {stats.text}")
        except Exception as e:
            print(f"[ERROR] Tidak bisa ambil stats: {e}")


if __name__ == "__main__":
    asyncio.run(main())