# 🏔️ Mountain Network Project — README

> เครือข่ายภูเขาสูงจำลอง บน Podman — 13 nodes, DTN, QoS, Energy Simulation

---

## 📋 สารบัญ
- [ภาพรวม](#ภาพรวม)
- [โครงสร้างไฟล์](#โครงสร้างไฟล์)
- [สำหรับ Architecture](#-สำหรับ-architecture)
- [สำหรับ Specialist](#-สำหรับ-specialist)
- [สำหรับ DevOps/IaC](#-สำหรับ-devopsiac)
- [สำหรับ Tester](#-สำหรับ-tester)

---

## ภาพรวม

โปรเจกต์นี้จำลองเครือข่ายภูเขาสูงบนเครื่องเดียว โดยใช้ Podman containers แทน router/server จริง

```
Internet Gateway (1)
        │
  ┌─────┼─────┐
Summit Alpha  Beta  Gamma  (3)
        │
  ┌─────┼─────┐
Relay North  Center  East  (3)
        │
  ┌─────┼─────┐
Village A  B  C  D         (4)
        │
Sensor Cluster 1  2        (2)
─────────────────────────
รวม 13 nodes
```

---

## โครงสร้างไฟล์

```
mountain-network/
├── docker-compose.yml    ← topology ทั้งหมด (networks + containers)
├── monitor.py            ← AI monitoring script (รันนอก container)
└── node/
    ├── app.py            ← code หลักของทุก node
    ├── Dockerfile        ← blueprint สร้าง container
    └── requirements.txt  ← Python libraries
```

---

## 🏛️ สำหรับ Architecture

### 3-Layer Design

| Layer | Nodes | หน้าที่ |
|---|---|---|
| **B — Backbone** | Internet Gateway, Summit Alpha/Beta/Gamma | เชื่อมต่อหลัก, routing |
| **B/C — Relay** | Relay North/Center/East | DTN buffer, จุดกระจาย |
| **A — Access** | Village A/B/C/D, Sensor 1/2 | ผู้ใช้ปลายทาง |

### Mesh Topology
- ทุก node มีอย่างน้อย **2 เส้นทาง** ไปยัง backbone
- ตัดลิงก์เดียว → ระบบยังทำงานได้ผ่านเส้นทางสำรอง
- ต้องตัด **2 เส้นขึ้นไป** พร้อมกัน ถึงจะแยก node ออกจากระบบได้

### DTN (Delay-Tolerant Networking)
- ถ้าส่งไม่ได้ → **เก็บใน queue** แทนที่จะ error
- retry อัตโนมัติทุก **30 วินาที**
- ข้อมูลไม่หายแม้ลิงก์จะขาด

### Traffic Classes (QoS)
```
Priority 1: emergency   ← ผ่านได้เสมอ แม้ low power
Priority 2: telemetry   ← ถูกบล็อกเมื่อ low power
Priority 3: normal      ← ถูกบล็อกเมื่อ low power
```

### Energy Simulation
```
energy ≥ 50%  → normal mode  (รับทุก traffic)
energy 20-49% → monitoring   (แจ้งเตือนแต่ยังรับปกติ)
energy < 20%  → low power    (รับแค่ emergency)
```

---

## 🔬 สำหรับ Specialist

### API Endpoints (ทุก node มีเหมือนกัน)

| Method | Endpoint | หน้าที่ |
|---|---|---|
| GET | `/health` | สถานะ node, energy, queue size |
| POST | `/send` | ส่งข้อความไปหา neighbor |
| POST | `/receive` | รับข้อความ (มี low power check) |
| GET | `/log` | ดูข้อความที่รับมาทั้งหมด |
| GET | `/queue` | ดู DTN queue |
| POST | `/power` | เปิด/ปิด low power mode manual |
| GET | `/power` | ดูสถานะ power mode |
| POST | `/energy` | ตั้งค่า energy level (0-100) |
| GET | `/energy` | ดู energy level ปัจจุบัน |

### Message Format
```json
{
  "origin": "village-a",
  "destination": "relay-north",
  "content": "ข้อความ",
  "priority": "emergency|telemetry|normal",
  "timestamp": "2026-03-13T20:00:00"
}
```

### Low Power Logic
```
POST /receive ถูกเรียก
        ↓
เช็ค low_power_mode
        ↓
priority = normal/telemetry → rejected (403)
priority = emergency        → accepted ✅
```

### Energy Auto-trigger
```
POST /energy {"level": 15}
        ↓
energy < 20 → low_power_mode = True  (อัตโนมัติ)
energy ≥ 50 → low_power_mode = False (อัตโนมัติ)
```

---

## 🛠️ สำหรับ DevOps/IaC

### Requirements
- Podman ≥ 3.4
- podman-compose ≥ 1.0
- Python 3.11+

### Commands หลัก

```bash
# Build และรัน (ครั้งแรก หรือหลังแก้โค้ด)
podman-compose up -d --build

# หยุดทั้งหมด
podman-compose down

# ดูสถานะ
podman ps --format "table {{.Names}}\t{{.Status}}"

# ดู log ของ container
podman logs relay-center

# รัน command ใน container
podman exec relay-center python3 -c "..."
```

### Network Architecture

| Network | Subnet | ใช้กับ |
|---|---|---|
| `backbone_net` | 172.20.0.0/24 | Summit + Gateway |
| `access_net_north` | 172.21.0.0/24 | Alpha, Relay North/Center, Village A/B |
| `access_net_east` | 172.22.0.0/24 | Gamma, Relay Center/East, Village C/D |
| `access_net_south` | 172.23.0.0/24 | Relay Center, Village B/C |
| `sensor_net` | 172.24.0.0/24 | Sensor Cluster 1/2 |

### จำลอง Link Failure

```bash
# ตัดลิงก์
podman network disconnect mountain-network_access_net_north relay-center

# ต่อลิงก์กลับ
podman network connect mountain-network_access_net_north relay-center
```

### Port Mapping (host → container)

| Port | Node |
|---|---|
| 9000 | internet-gateway |
| 9001 | village-a |
| 9002 | village-b |
| 9003 | village-c |
| 9004 | village-d |
| 9005 | sensor-cluster-1 |
| 9006 | sensor-cluster-2 |

> **หมายเหตุ:** Summit และ Relay ไม่มี port expose ออกมา ต้องใช้ `podman exec` เข้าถึง

---

## 🧪 สำหรับ Tester

### Test 1 — Normal Operation
```bash
# ส่งข้อความปกติ
curl -X POST http://localhost:9001/send \
  -H "Content-Type: application/json" \
  -d '{"origin":"village-a","destination":"relay-north","content":"Hello!","priority":"normal"}'

# ตรวจสอบว่าถึงปลายทาง
podman exec relay-north python3 -c \
  "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"

# ✅ Expected: status = "delivered"
```

### Test 2 — Mesh Redundancy (Single Link Failure)
```bash
# ตัด 1 เส้น
podman network disconnect mountain-network_access_net_north relay-center

# ส่งข้อความ — ยังควรผ่านได้ผ่านเส้นอื่น
curl -X POST http://localhost:9002/send \
  -H "Content-Type: application/json" \
  -d '{"origin":"village-b","destination":"relay-center","content":"Test","priority":"normal"}'

# ✅ Expected: status = "delivered" (ผ่าน access_net_south)

# ต่อลิงก์กลับ
podman network connect mountain-network_access_net_north relay-center
```

### Test 3 — DTN Store-and-Forward
```bash
# ตัด 2 เส้น (ทำให้ relay-center หายไปจาก network)
podman network disconnect mountain-network_access_net_north relay-center
podman network disconnect mountain-network_access_net_south relay-center

# ส่งข้อความ — ควร queued
curl -X POST http://localhost:9002/send \
  -H "Content-Type: application/json" \
  -d '{"origin":"village-b","destination":"relay-center","content":"DTN test","priority":"emergency"}'

# ✅ Expected: status = "queued"

# เช็ค queue
curl -s http://localhost:9002/queue

# ต่อลิงก์กลับ แล้วรอ 30 วินาที
podman network connect mountain-network_access_net_south relay-center
sleep 35

# เช็คว่าส่งถึงแล้ว
podman exec relay-center python3 -c \
  "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"

# ✅ Expected: ข้อความปรากฏใน log
```

### Test 4 — Power Degradation
```bash
# ตั้ง energy ต่ำที่ relay-center
podman exec relay-center python3 -c "
import urllib.request, json
data = json.dumps({'level': 15}).encode()
req = urllib.request.Request('http://localhost:8000/energy', data=data, headers={'Content-Type': 'application/json'}, method='POST')
print(urllib.request.urlopen(req).read().decode())
"

# ส่ง normal — ควรถูกปฏิเสธ
curl -X POST http://localhost:9002/send \
  -H "Content-Type: application/json" \
  -d '{"origin":"village-b","destination":"relay-center","content":"Weather","priority":"normal"}'
# ✅ Expected: status = "rejected"

# ส่ง emergency — ควรผ่าน
curl -X POST http://localhost:9002/send \
  -H "Content-Type: application/json" \
  -d '{"origin":"village-b","destination":"relay-center","content":"EMERGENCY!","priority":"emergency"}'
# ✅ Expected: status = "delivered"
```

### รัน AI Monitor
```bash
# รันใน terminal แยก
python3 monitor.py

# จะเช็คทุก 20 วินาที และแจ้งเตือนเมื่อ:
# 🔴 CRITICAL — node offline หรือ emergency ค้างใน queue
# 🟡 WARNING  — queue ใหญ่ผิดปกติ (≥ 3 messages)
```

---

## 🔑 Key Concepts สรุปสั้น

| Concept | คืออะไร | ในโปรเจกต์นี้ |
|---|---|---|
| **Mesh** | หลายเส้นทาง | 5 networks เชื่อมกันหลายทาง |
| **DTN** | เก็บข้อความรอส่ง | `dtn_queue` + `retry_loop` |
| **QoS** | จัดลำดับ traffic | emergency > telemetry > normal |
| **Energy** | จำลองพลังงานจำกัด | `energy_level` → `low_power_mode` |
| **AI Monitor** | ตรวจจับความผิดปกติ | `monitor.py` เช็คทุก 20 วินาที |

---

*Mountain Network Project — Computer Networks Course*
*Team: 5 Members | Duration: 4 Weeks*
