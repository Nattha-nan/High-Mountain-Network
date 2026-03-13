import subprocess, time, httpx, asyncio, json

def curl(method, url, data=None):
    """Helper — แทน curl command"""
    cmd = ["curl", "-s", "-X", method, url, "-H", "Content-Type: application/json"]
    if data:
        cmd += ["-d", json.dumps(data)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return json.loads(result.stdout)
    except:
        return result.stdout

def podman_exec(container, python_code):
    """Helper — แทน podman exec"""
    result = subprocess.run(
        ["podman", "exec", container, "python3", "-c", python_code],
        capture_output=True, text=True
    )
    try:
        return json.loads(result.stdout)
    except:
        return result.stdout

def network(action, network_name, container):
    """Helper — connect/disconnect network"""
    subprocess.run(
        ["podman", "network", action, f"mountain-network_{network_name}", container],
        capture_output=True
    )

def pause(msg=""):
    input(f"\n  {'─'*50}\n  ⏎  {msg} — กด Enter เพื่อดำเนินต่อ...")
    print()

def header(title):
    print(f"\n{'='*55}")
    print(f"  🧪 {title}")
    print(f"{'='*55}")

def show(label, result, expect=None):
    status = result.get("status", "") if isinstance(result, dict) else ""
    icon = "✅" if (expect and status == expect) else "📋"
    print(f"  {icon} {label}: {json.dumps(result, ensure_ascii=False)}")
    if expect:
        ok = "✅ PASS" if status == expect else "❌ FAIL"
        print(f"     → Expected: {expect} | Got: {status} | {ok}")

# ══════════════════════════════════════════════════
print("\n🏔️  Mountain Network — Demo Script")
print("    กด Enter เพื่อเดินหน้าแต่ละขั้นตอน")
pause("เริ่ม Demo")

# ══════════════════════════════════════════════════
header("TEST 1 — Normal Operation")
print("  ส่งข้อความปกติจาก village-a → relay-north")

pause("ส่งข้อความ")
result = curl("POST", "http://localhost:9001/send", {
    "origin": "village-a",
    "destination": "relay-north",
    "content": "Hello from Village A!",
    "priority": "normal"
})
show("Send", result, expect="delivered")

pause("เช็ค log ที่ relay-north")
log = podman_exec("relay-north",
    "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())")
if isinstance(log, dict):
    msgs = log.get("messages", [])
    print(f"  📋 relay-north มี {len(msgs)} ข้อความใน log")
    for m in msgs[-1:]:
        print(f"     → [{m['priority']}] {m['content']}")

# ══════════════════════════════════════════════════
header("TEST 2 — Mesh Redundancy (Single Link Failure)")
print("  ตัด 1 เส้น → ระบบควรหาเส้นทางสำรองได้")

pause("ตัดลิงก์ access_net_north ออกจาก relay-center")
network("disconnect", "access_net_north", "relay-center")
print("  ✂️  ตัดลิงก์แล้ว")

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

# ══════════════════════════════════════════════════
header("TEST 3 — DTN Store-and-Forward")
print("  ตัด 2 เส้น → ข้อความควร queued แล้ว retry อัตโนมัติ")

pause("ตัดลิงก์ทั้ง 2 เส้นของ relay-center")
network("disconnect", "access_net_north", "relay-center")
network("disconnect", "access_net_south", "relay-center")
print("  ✂️  ตัด 2 ลิงก์แล้ว")

pause("ส่งข้อความ — ควร queued")
result = curl("POST", "http://localhost:9002/send", {
    "origin": "village-b",
    "destination": "relay-center",
    "content": "DTN test — store and forward",
    "priority": "emergency"
})
show("Send", result, expect="queued")

pause("เช็ค queue")
q = curl("GET", "http://localhost:9002/queue")
print(f"  📦 queue มี {len(q.get('queued', []))} ข้อความรออยู่")

pause("ต่อลิงก์กลับ แล้วรอ DTN retry 35 วินาที...")
network("connect", "access_net_south", "relay-center")
print("  🔗 ต่อลิงก์กลับแล้ว รอ 35 วินาที...", end="", flush=True)
for i in range(35):
    time.sleep(1)
    print(".", end="", flush=True)
print(" done!")

log = podman_exec("relay-center",
    "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())")
if isinstance(log, dict):
    msgs = [m for m in log.get("messages", []) if "DTN test" in m.get("content", "")]
    icon = "✅ PASS" if msgs else "❌ FAIL"
    print(f"  {icon} DTN retry: ข้อความถึง relay-center {'แล้ว' if msgs else 'ยังไม่ถึง'}")

# ══════════════════════════════════════════════════
header("TEST 4 — Power Degradation")
print("  ลด energy < 20% → normal ถูกบล็อก, emergency ผ่าน")

pause("ตั้ง energy = 15% ที่ relay-center")
result = podman_exec("relay-center", """
import urllib.request, json
data = json.dumps({'level': 15}).encode()
req = urllib.request.Request('http://localhost:8000/energy', data=data, headers={'Content-Type': 'application/json'}, method='POST')
print(urllib.request.urlopen(req).read().decode())
""")
if isinstance(result, dict):
    print(f"  ⚡ energy={result.get('energy_level')}% | low_power={result.get('low_power_mode')}")

pause("ส่ง normal — ควร rejected")
result = curl("POST", "http://localhost:9002/send", {
    "origin": "village-b",
    "destination": "relay-center",
    "content": "Weather update",
    "priority": "normal"
})
show("Normal traffic", result, expect="rejected")

pause("ส่ง emergency — ควร delivered")
result = curl("POST", "http://localhost:9002/send", {
    "origin": "village-b",
    "destination": "relay-center",
    "content": "EMERGENCY! Landslide detected!",
    "priority": "emergency"
})
show("Emergency traffic", result, expect="delivered")

# Reset
podman_exec("relay-center", """
import urllib.request, json
data = json.dumps({'level': 100}).encode()
req = urllib.request.Request('http://localhost:8000/energy', data=data, headers={'Content-Type': 'application/json'}, method='POST')
urllib.request.urlopen(req).read()
""")
print("  🔋 Reset energy กลับ 100% แล้ว")

# ══════════════════════════════════════════════════
header("TEST 5 — QoS Priority Queue")
print("  ส่ง normal ก่อน แต่ emergency ควรถึงปลายทางก่อน")

pause("ตัดลิงก์ relay-center")
network("disconnect", "access_net_north", "relay-center")
network("disconnect", "access_net_south", "relay-center")

pause("ส่ง 3 ข้อความ: normal → telemetry → emergency")
curl("POST", "http://localhost:9002/send", {
    "origin": "village-b", "destination": "relay-center",
    "content": "Normal update", "priority": "normal"
})
curl("POST", "http://localhost:9002/send", {
    "origin": "village-b", "destination": "relay-center",
    "content": "Sensor reading", "priority": "telemetry"
})
curl("POST", "http://localhost:9002/send", {
    "origin": "village-b", "destination": "relay-center",
    "content": "EMERGENCY! Flood!", "priority": "emergency"
})
print("  📤 ส่ง 3 ข้อความเข้า queue แล้ว")

q = curl("GET", "http://localhost:9002/queue")
print(f"  📦 queue: {[m['priority'] for m in q.get('queued', [])]}")

pause("ต่อลิงก์กลับ รอ QoS retry 35 วินาที...")
network("connect", "access_net_south", "relay-center")
print("  รอ...", end="", flush=True)
for i in range(35):
    time.sleep(1)
    print(".", end="", flush=True)
print(" done!")

log = podman_exec("relay-center",
    "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())")
if isinstance(log, dict):
    msgs = log.get("messages", [])
    recent = msgs[-3:] if len(msgs) >= 3 else msgs
    print("  📋 ลำดับที่ถึง relay-center:")
    for i, m in enumerate(recent, 1):
        print(f"     {i}. [{m['priority']}] {m['content']}")
    if recent and recent[0].get("priority") == "emergency":
        print("  ✅ PASS — emergency มาก่อน!")
    else:
        print("  ❌ FAIL — ลำดับไม่ถูกต้อง")

network("connect", "access_net_north", "relay-center")

# ══════════════════════════════════════════════════
print(f"\n{'='*55}")
print("  🏆 Demo เสร็จสิ้น!")
print("  ทุก test cases ครบตาม architecture_spec.md")
print(f"{'='*55}\n")