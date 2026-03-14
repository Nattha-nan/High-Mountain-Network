"""
🏔️ Mountain Network — Demo Script v2
รองรับ Docker Desktop (Windows PowerShell / macOS / Linux)

วิธีใช้:
    python demo_v2.py

Requirements:
    - Docker Desktop รันอยู่
    - podman-compose up -d --build (หรือ docker-compose up -d --build) เสร็จแล้ว
    - pip install httpx
"""

import subprocess, time, httpx, json, sys, shutil

# ══════════════════════════════════════════════════
# Auto-detect: Docker หรือ Podman
# ══════════════════════════════════════════════════

def detect_engine():
    if shutil.which("docker"):
        return "docker"
    elif shutil.which("podman"):
        return "podman"
    else:
        print("❌ ไม่พบ docker หรือ podman — กรุณาติดตั้ง Docker Desktop ก่อน")
        sys.exit(1)

ENGINE = "docker"  # v2: ใช้ docker เท่านั้น
NETWORK_PREFIX = "mountain-network"

print(f"🐳 Using engine: {ENGINE}")

# ══════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════

def curl(method, url, data=None):
    """ส่ง HTTP request"""
    try:
        with httpx.Client(timeout=5.0) as client:
            if method == "GET":
                r = client.get(url)
            else:
                r = client.post(url, json=data)
            return r.json()
    except Exception as e:
        return {"error": str(e)}

def container_exec(container, python_code):
    """รัน python3 ใน container"""
    result = subprocess.run(
        [ENGINE, "exec", container, "python3", "-c", python_code],
        capture_output=True,
        text=True,
        encoding="utf-8",      # ← เพิ่มบรรทัดนี้
        errors="replace"       # ← เพิ่มบรรทัดนี้ (ถ้าอ่านไม่ได้ให้แทนด้วย ? แทน crash)
    )
    try:
        return json.loads(result.stdout)
    except:
        return result.stdout.strip() or result.stderr.strip()

def network(action, network_name, container):
    """connect/disconnect container ออกจาก network"""
    full_name = f"{NETWORK_PREFIX}_{network_name}"
    result = subprocess.run(
        [ENGINE, "network", action, full_name, container],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  ⚠️  network {action} warning: {result.stderr.strip()}")

def set_energy(container, level):
    """ตั้งค่า energy level ใน container"""
    code = f"""
import urllib.request, json
data = json.dumps({{'level': {level}}}).encode()
req = urllib.request.Request(
    'http://localhost:8000/energy', data=data,
    headers={{'Content-Type': 'application/json'}}, method='POST'
)
print(urllib.request.urlopen(req).read().decode())
"""
    return container_exec(container, code)

def get_log(container):
    """ดู message log ของ container"""
    code = "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"
    return container_exec(container, code)

# ══════════════════════════════════════════════════
# UI Helpers
# ══════════════════════════════════════════════════

def pause(msg=""):
    input(f"\n  {'─'*50}\n  ⏎  {msg} — กด Enter เพื่อดำเนินต่อ...")
    print()

def header(title):
    print(f"\n{'='*58}")
    print(f"  🧪 {title}")
    print(f"{'='*58}")

def show(label, result, expect=None):
    if isinstance(result, dict):
        status = result.get("status", "")
        print(f"  📋 {label}:")
        print(f"     {json.dumps(result, ensure_ascii=False)}")
        if expect:
            ok = "✅ PASS" if status == expect else "❌ FAIL"
            print(f"     → Expected: '{expect}' | Got: '{status}' | {ok}")
    else:
        print(f"  📋 {label}: {result}")

def wait_with_dots(seconds):
    print(f"  ⏳ รอ {seconds} วินาที", end="", flush=True)
    for _ in range(seconds):
        time.sleep(1)
        print(".", end="", flush=True)
    print(" done!")

# ══════════════════════════════════════════════════
# Startup Check
# ══════════════════════════════════════════════════

def check_services():
    print("\n🔍 ตรวจสอบ services...")
    nodes = {
        "internet-gateway": 9000,
        "village-a": 9001,
        "village-b": 9002,
    }
    all_ok = True
    for name, port in nodes.items():
        result = curl("GET", f"http://localhost:{port}/health")
        if "error" in result:
            print(f"  ❌ {name} — ไม่ตอบสนอง ({result['error']})")
            all_ok = False
        else:
            print(f"  ✅ {name} — online")

    if not all_ok:
        print("\n⚠️  บาง service ไม่ทำงาน")
        print("   รัน: docker-compose up -d --build แล้วลองใหม่")
        sys.exit(1)
    print("  ✅ Services พร้อมทั้งหมด!\n")

# ══════════════════════════════════════════════════
# MAIN DEMO
# ══════════════════════════════════════════════════

print("\n" + "="*58)
print("  🏔️  Mountain Network — Demo Script v2 (Docker)")
print("      กด Enter เพื่อเดินหน้าแต่ละขั้นตอน")
print("="*58)

check_services()
pause("เริ่ม Demo")

# ──────────────────────────────────────────────────
header("TEST 1 — Normal Operation")
print("  ส่งข้อความปกติจาก village-a → relay-north")
print("  คาดหวัง: delivered ทันที")

pause("ส่งข้อความ")
result = curl("POST", "http://localhost:9001/send", {
    "origin": "village-a",
    "destination": "relay-north",
    "content": "Hello from Village A!",
    "priority": "normal"
})
show("Send result", result, expect="delivered")

pause("เช็ค log ที่ relay-north")
log = get_log("relay-north")
if isinstance(log, dict):
    msgs = log.get("messages", [])
    print(f"  📋 relay-north มี {len(msgs)} ข้อความใน log")
    for m in msgs[-1:]:
        print(f"     → [{m['priority']}] {m['content']}")

# ──────────────────────────────────────────────────
header("TEST 2 — Mesh Redundancy (Single Link Failure)")
print("  ตัด 1 เส้น → ระบบควรหาเส้นทางสำรองได้อัตโนมัติ")
print("  คาดหวัง: delivered ผ่านเส้นทางอื่น")

pause("ตัดลิงก์ access_net_north ออกจาก relay-center")
network("disconnect", "access_net_north", "relay-center")
print("  ✂️  ตัดลิงก์ access_net_north แล้ว")
print("  📍 relay-center ยังเชื่อมกับ village-b ผ่าน access_net_south อยู่")

pause("ส่งข้อความ village-b → relay-center")
result = curl("POST", "http://localhost:9002/send", {
    "origin": "village-b",
    "destination": "relay-center",
    "content": "Mesh redundancy test",
    "priority": "normal"
})
show("Send (ผ่าน access_net_south แทน)", result, expect="delivered")

pause("ต่อลิงก์กลับ")
network("connect", "access_net_north", "relay-center")
print("  🔗 ต่อลิงก์กลับแล้ว")

# ──────────────────────────────────────────────────
header("TEST 3 — DTN Store-and-Forward")
print("  ตัด 2 เส้น → ข้อความควร queued แล้ว retry อัตโนมัติ")
print("  คาดหวัง: queued → delivered เมื่อลิงก์กลับมา")

pause("ตัดลิงก์ทั้ง 2 เส้นของ relay-center")
network("disconnect", "access_net_north", "relay-center")
network("disconnect", "access_net_south", "relay-center")
print("  ✂️  ตัด 2 ลิงก์แล้ว — relay-center ไม่ติดต่อได้")

pause("ส่งข้อความ — ควรถูกเก็บใน DTN queue")
result = curl("POST", "http://localhost:9002/send", {
    "origin": "village-b",
    "destination": "relay-center",
    "content": "DTN test — store and forward",
    "priority": "emergency"
})
show("Send", result, expect="queued")

pause("เช็ค DTN queue ของ village-b")
q = curl("GET", "http://localhost:9002/queue")
queued = q.get("queued", [])
print(f"  📦 queue มี {len(queued)} ข้อความรออยู่:")
for m in queued:
    print(f"     → [{m['priority']}] {m['content']}")

pause("ต่อลิงก์กลับ แล้วรอ DTN retry อัตโนมัติ (35 วินาที)")
network("connect", "access_net_south", "relay-center")
print("  🔗 ต่อลิงก์กลับแล้ว")
wait_with_dots(35)

log = get_log("relay-center")
if isinstance(log, dict):
    msgs = [m for m in log.get("messages", []) if "DTN test" in m.get("content", "")]
    if msgs:
        print("  ✅ PASS — DTN retry สำเร็จ! ข้อความถึง relay-center แล้ว")
    else:
        print("  ❌ FAIL — ข้อความยังไม่ถึง relay-center")

network("connect", "access_net_north", "relay-center")

# ──────────────────────────────────────────────────
header("TEST 4 — Power Degradation")
print("  ลด energy < 20% → normal ถูกบล็อกอัตโนมัติ, emergency ผ่าน")

pause("ตั้ง energy = 15% ที่ relay-center")
result = set_energy("relay-center", 15)
if isinstance(result, dict):
    print(f"  ⚡ energy={result.get('energy_level')}% | low_power={result.get('low_power_mode')}")
    print(f"  💬 {result.get('message', '')}")

pause("ส่ง normal traffic — ควรถูก rejected")
result = curl("POST", "http://localhost:9002/send", {
    "origin": "village-b",
    "destination": "relay-center",
    "content": "Weather update (normal)",
    "priority": "normal"
})
show("Normal traffic", result, expect="rejected")

pause("ส่ง emergency traffic — ควรผ่านได้")
result = curl("POST", "http://localhost:9002/send", {
    "origin": "village-b",
    "destination": "relay-center",
    "content": "EMERGENCY! Landslide detected!",
    "priority": "emergency"
})
show("Emergency traffic", result, expect="delivered")

pause("Reset energy กลับ 100%")
set_energy("relay-center", 100)
print("  🔋 Reset energy = 100% แล้ว")

# ──────────────────────────────────────────────────
header("TEST 5 — QoS Priority Queue")
print("  ส่ง normal → telemetry → emergency เข้า queue")
print("  คาดหวัง: emergency ถึงปลายทางก่อนแม้เข้าคิวทีหลัง")

pause("ตัดลิงก์ relay-center ทั้งหมด")
network("disconnect", "access_net_north", "relay-center")
network("disconnect", "access_net_south", "relay-center")
print("  ✂️  ตัด 2 ลิงก์แล้ว")

pause("ส่ง 3 ข้อความตามลำดับ: normal → telemetry → emergency")
curl("POST", "http://localhost:9002/send", {
    "origin": "village-b", "destination": "relay-center",
    "content": "1. Normal update", "priority": "normal"
})
print("  📤 ส่ง [normal] แล้ว")

curl("POST", "http://localhost:9002/send", {
    "origin": "village-b", "destination": "relay-center",
    "content": "2. Sensor reading 42C", "priority": "telemetry"
})
print("  📤 ส่ง [telemetry] แล้ว")

curl("POST", "http://localhost:9002/send", {
    "origin": "village-b", "destination": "relay-center",
    "content": "3. EMERGENCY! Flood!", "priority": "emergency"
})
print("  📤 ส่ง [emergency] แล้ว (เข้าคิวทีหลังสุด)")

q = curl("GET", "http://localhost:9002/queue")
order = [m['priority'] for m in q.get('queued', [])]
print(f"\n  📦 ลำดับใน queue ตอนนี้: {order}")
print("     (ยังเรียงตามเวลาที่เข้ามา รอดู relay หลัง retry)")

pause("ต่อลิงก์กลับ รอ QoS retry 35 วินาที")
network("connect", "access_net_south", "relay-center")
print("  🔗 ต่อลิงก์กลับแล้ว")
wait_with_dots(35)

log = get_log("relay-center")
if isinstance(log, dict):
    msgs = log.get("messages", [])
    recent = [m for m in msgs if m.get("origin") == "village-b"][-3:]
    print("\n  📋 ลำดับที่ถึง relay-center:")
    for i, m in enumerate(recent, 1):
        print(f"     {i}. [{m['priority']}] {m['content']}")
    if recent and recent[0].get("priority") == "emergency":
        print("  ✅ PASS — emergency มาก่อน!")
    else:
        print("  ⚠️  ลำดับอาจไม่ตรงตามคาด — เช็ค log เพิ่มเติม")

network("connect", "access_net_north", "relay-center")

# ══════════════════════════════════════════════════
print(f"\n{'='*58}")
print("  🏆 Demo เสร็จสิ้น!")
print("  ครอบคลุมทุก test case ตาม architecture_spec.md")
print(f"{'='*58}\n")
