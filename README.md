# High-Mountain-Network
# 🏔️ High Mountain Network Project — README

> **Course:** Computer Networks (Undergraduate)  
> **Team:** 5 Members | Architecture · Engineer · Specialist · DevOps · Tester

### New Network

https://drive.google.com/drive/folders/1rHFE-OYRYLAQ6IIp_zsCRfgqoRRXAA4D

### Sprint Alpha + 1

https://drive.google.com/drive/folders/1vQBkmgv6CHOAUs_xkw_hhM3xhN4i0VlQ

### Final Project Presentation Slide

https://www.canva.com/design/DAHEMPm_MvI/Hb9vQQhkV9Vy5KGcmRfINA/edit?utm_content=DAHEMPm_MvI&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton

#### ⩥ การ Run โปรเจค

โหลดโฟลเดอร์ mountain-network

ดูวิธี set up ที่ไฟล์ WINDOWS_SETUP.md

---

## 📖 โปรเจกต์นี้คืออะไร?

จำลอง **เครือข่ายภูเขาสูง** บนเครื่องเดียว โดยใช้ Podman containers แทนอุปกรณ์จริง

เครือข่ายนี้ออกแบบมาเพื่อ:
- ทนต่อลิงก์ขาดได้ (ไม่พังทั้งระบบ)
- ส่งข้อความได้แม้ไม่มีสัญญาณชั่วคราว (DTN)
- จัดลำดับความสำคัญ traffic (QoS)
- ประหยัดพลังงานเมื่อแบตต่ำ (Energy Mode)

## ภาพรวมสถาปัตยกรรม (โครงสร้างโปรโตคอล)

Application Layer
- แอปฉุกเฉิน / ระบบ monitoring
  
Transport Layer
- TCP/UDP (จำลอง)

Network Layer 
- OSPF + DTN Overlay

Data Link Layer 
- Ethernet/Wi-Fi (จำลอง)

Physical Layer
- ลิงก์ไร้สายบนภูเขา

---

## 🗺️ Topology — 13 Nodes, 3 ชั้น

```
                   Internet Gateway (สีส้ม)
                          │
          ┌───────────────┼───────────────┐
     Summit Alpha     Summit Beta     Summit Gamma   ← Layer B: Backbone
          │               │               │
     Relay North    Relay Center     Relay East      ← Layer B/C: DTN Relay
          │               │               │
    Village A/B      Village B/C      Village C/D    ← Layer A: Access
          │                               │
   Sensor Cluster 1               Sensor Cluster 2  ← IoT
```

### Networks (5 วง)

| Network | Subnet | หน้าที่ |
|---|---|---|
| backbone_net | 172.20.0.0/24 | Summit ↔ Summit |
| access_net_north | 172.21.0.0/24 | ฝั่งเหนือ (Alpha, Relay North, Village A/B) |
| access_net_east | 172.22.0.0/24 | ฝั่งตะวันออก (Gamma, Relay East, Village C/D) |
| access_net_south | 172.23.0.0/24 | กลาง (Relay Center, Village B/C) |
| sensor_net | 172.24.0.0/24 | IoT Sensors |

---

## 📁 โครงสร้างไฟล์

```
mountain-network/
├── docker-compose.yml    ← topology ทั้งหมด (13 nodes, 5 networks)
├── monitor.py            ← AI Monitoring script
├── demo.py               ← Demo script สำหรับพรีเซนต์
└── node/
    ├── app.py            ← โค้ดหลักของทุก node
    ├── Dockerfile        ← สูตรสร้าง container
    └── requirements.txt  ← Python libraries
```

---

## 🚀 Quick Start (DevOps/IaC)

### Requirements
- Podman ≥ 3.4
- podman-compose ≥ 1.0
- Python 3.11+

### รัน

```bash
cd mountain-network

# Build และรัน
podman-compose up -d --build

# เช็คสถานะ
podman ps --format "table {{.Names}}\t{{.Status}}"

# หยุด
podman-compose down
```

### Ports ที่ expose ออกมา

| Port | Node |
|---|---|
| 9000 | internet-gateway |
| 9001 | village-a |
| 9002 | village-b |
| 9003 | village-c |
| 9004 | village-d |
| 9005 | sensor-cluster-1 |
| 9006 | sensor-cluster-2 |

---

## 🔌 API Endpoints (Specialist)

ทุก node มี endpoints เดียวกัน:

| Method | Endpoint | หน้าที่ |
|---|---|---|
| GET | `/health` | เช็คสถานะ node, energy, queue size |
| POST | `/send` | ส่งข้อความไปหา node อื่น |
| POST | `/receive` | รับข้อความ (เรียกโดย node อื่น) |
| GET | `/log` | ดูข้อความที่รับมาทั้งหมด |
| GET | `/queue` | ดู DTN queue (ข้อความรอส่ง) |
| POST | `/power` | เปิด/ปิด low power mode |
| GET | `/power` | เช็ค power mode |
| POST | `/energy` | ตั้งระดับพลังงาน 0-100% |
| GET | `/energy` | เช็คระดับพลังงาน |

### ตัวอย่าง Request

```bash
# เช็คสุขภาพ node
curl http://localhost:9001/health

# ส่งข้อความ
curl -X POST http://localhost:9001/send \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "village-a",
    "destination": "relay-north",
    "content": "Hello!",
    "priority": "normal"
  }'

# Priority มี 3 ระดับ: emergency | telemetry | normal
```

---

## 🧠 Concepts หลัก (Architecture)

### 1. Mesh Topology
แต่ละ node มีอย่างน้อย 2 เส้นทางเชื่อมต่อ → ตัด 1 เส้น ระบบยังทำงานได้

### 2. DTN — Delay-Tolerant Networking
ถ้าส่งไม่ได้ → เก็บใน queue → retry อัตโนมัติทุก 30 วินาที

```
ปกติ:     village-b ──→ relay-center  ✅ delivered
ลิงก์ขาด: village-b ──→ [queue] ──→ retry เมื่อลิงก์กลับ ✅
```

### 3. QoS Priority
ใน DTN queue จะเรียงตาม priority ก่อนส่ง:
```
emergency (0) → telemetry (1) → normal (2)
```

### 4. Energy Mode
```
energy ≥ 50%  → normal mode  (รับทุก traffic)
energy < 20%  → low power    (รับแค่ emergency)
```

---

## 🧪 Testing Scenarios (Tester)

### วิธีดู log ของ node ที่ไม่มี port expose

```bash
podman exec relay-center python3 -c \
  "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"
```

### วิธีจำลองลิงก์ขาด

```bash
# ตัดลิงก์
podman network disconnect mountain-network_access_net_north relay-center

# ต่อลิงก์กลับ
podman network connect mountain-network_access_net_north relay-center
```

### Test Cases ครบ 4 ชุด

| Test | วิธีทดสอบ | ผลที่คาดหวัง |
|---|---|---|
| Normal Operation | ส่งข้อความปกติ | `delivered` |
| Single Link Failure | ตัด 1 เส้น แล้วส่ง | `delivered` (ผ่านเส้นอื่น) |
| DTN Store-and-Forward | ตัด 2 เส้น → ส่ง → ต่อกลับ | `queued` → retry อัตโนมัติ |
| Power Degradation | set energy 15% → ส่ง normal | `rejected` |

---

## 🤖 AI Monitor

```bash
# รัน monitor (อัปเดตทุก 20 วินาที)
python3 monitor.py
```

ตรวจจับ anomaly 3 ประเภท:
- 🔴 **CRITICAL** — node offline
- 🔴 **CRITICAL** — emergency ค้างใน queue
- 🟡 **WARNING** — queue ใหญ่ผิดปกติ (≥ 3 messages)

---

## 🎬 Demo Script (สำหรับพรีเซนต์)

```bash
python3 demo.py
```

Script จะเดิน test ทีละขั้น กด Enter เพื่อดำเนินต่อ — แสดงผล PASS/FAIL อัตโนมัติ ครอบคลุมทุก test case

---

## 📚 ทฤษฎีที่ใช้อ้างอิง

| ทฤษฎี | ใช้ตรงไหน |
|---|---|
| OSI / TCP-IP Model | โครงสร้าง 3 ชั้น |
| DTN (Delay-Tolerant Networking) | Store-and-forward queue |
| Graph Theory | Mesh ≥ 2-connected |
| Queuing Theory | QoS priority ordering |
| Resilient Network Design | Multi-path routing |
| Edge Computing | Processing ที่แต่ละ node |


---

## Windows รันได้ แต่ต้องเลือกวิธี

**วิธีที่ 1 — Docker Desktop** (แนะนำสุด)
```
ติดตั้ง Docker Desktop
แล้วรัน docker-compose up -d --build
ได้เลย ไม่ต้องแก้อะไร
```
เพราะ `docker-compose.yml` เป็น format มาตรฐาน Docker อ่านได้ตรงๆ

---

**วิธีที่ 2 — Podman on Windows** (ที่ลองแล้วติดปัญหา)
```
ต้องติดตั้ง Podman Desktop + WSL2
บางครั้งมีปัญหา network driver
ยุ่งยากกว่า Docker Desktop
```

---

**วิธีที่ 3 — WSL2 + Ubuntu** (คล้าย Fedora มากที่สุด)
```
เปิด WSL2 ติดตั้ง Ubuntu
sudo apt install podman podman-compose
แล้วรันเหมือน Fedora เลย
```

---

## สรุป 𖤓

```
Docker Desktop   → ง่ายสุด แนะนำสำหรับ Windows
WSL2 + Ubuntu    → เหมือน Fedora เลย
Podman Windows   → ยุ่งยาก ไม่แนะนำ
```
