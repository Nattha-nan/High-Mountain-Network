import httpx
import asyncio
from datetime import datetime

# ทุก node ที่มี port expose ออกมา
NODES = {
    "internet-gateway":  "http://localhost:9000",
    "village-a":         "http://localhost:9001",
    "village-b":         "http://localhost:9002",
    "village-c":         "http://localhost:9003",
    "village-d":         "http://localhost:9004",
    "sensor-cluster-1":  "http://localhost:9005",
    "sensor-cluster-2":  "http://localhost:9006",
}

# threshold สำหรับ anomaly detection
QUEUE_THRESHOLD = 3      # queue เกิน 3 = ผิดปกติ
CHECK_INTERVAL  = 10     # เช็คทุก 20 วินาที

async def check_node(client: httpx.AsyncClient, name: str, url: str) -> dict:
    try:
        health = (await client.get(f"{url}/health", timeout=3.0)).json()
        queue  = (await client.get(f"{url}/queue",  timeout=3.0)).json()
        log    = (await client.get(f"{url}/log",    timeout=3.0)).json()
        return {
            "name":       name,
            "status":     "online",
            "role":       health.get("role"),
            "queue_size": len(queue.get("queued", [])),
            "msg_count":  len(log.get("messages", [])),
            "raw_queue":  queue.get("queued", []),
        }
    except Exception as e:
        return {
            "name":   name,
            "status": "offline",
            "error":  str(e),
        }

def detect_anomalies(results: list) -> list:
    anomalies = []
    for r in results:
        if r["status"] == "offline":
            anomalies.append({
                "severity": "CRITICAL",
                "node":     r["name"],
                "issue":    "Node offline — ไม่ตอบสนอง"
            })
            continue

        if r["queue_size"] >= QUEUE_THRESHOLD:
            anomalies.append({
                "severity": "WARNING",
                "node":     r["name"],
                "issue":    f"DTN queue ใหญ่ผิดปกติ ({r['queue_size']} messages) — ลิงก์อาจมีปัญหา"
            })

        # เช็ค emergency ที่ค้างใน queue
        emergency_stuck = [
            m for m in r.get("raw_queue", [])
            if m.get("priority") == "emergency"
        ]
        if emergency_stuck:
            anomalies.append({
                "severity": "CRITICAL",
                "node":     r["name"],
                "issue":    f"Emergency message ค้างใน queue {len(emergency_stuck)} ข้อความ!"
            })

    return anomalies

def print_report(results: list, anomalies: list):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"\n{'='*55}")
    print(f"  🏔️  Mountain Network Monitor — {now}")
    print(f"{'='*55}")

    for r in results:
        if r["status"] == "online":
            queue_warn = "⚠️ " if r["queue_size"] >= QUEUE_THRESHOLD else ""
            print(f"  ✅ {r['name']:<22} queue={queue_warn}{r['queue_size']}  msgs={r['msg_count']}")
        else:
            print(f"  ❌ {r['name']:<22} OFFLINE")

    if anomalies:
        print(f"\n  {'─'*51}")
        print(f"  🚨 Anomalies Detected:")
        for a in anomalies:
            icon = "🔴" if a["severity"] == "CRITICAL" else "🟡"
            print(f"  {icon} [{a['severity']}] {a['node']}: {a['issue']}")
    else:
        print(f"\n  ✨ No anomalies detected — network healthy")

    print(f"{'='*55}")

async def main():
    print("🏔️  Starting Mountain Network AI Monitor...")
    print(f"   Checking {len(NODES)} nodes every {CHECK_INTERVAL}s")
    print("   Press Ctrl+C to stop\n")

    async with httpx.AsyncClient() as client:
        while True:
            results   = await asyncio.gather(*[
                check_node(client, name, url)
                for name, url in NODES.items()
            ])
            anomalies = detect_anomalies(results)
            print_report(results, anomalies)
            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())