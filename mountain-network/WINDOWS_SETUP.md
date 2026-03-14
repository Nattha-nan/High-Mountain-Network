# 🪟 Windows Setup Guide — Mountain Network Project

> คู่มือสำหรับ Windows User โดยเฉพาะ  
> ใช้เวลาติดตั้งประมาณ 10-15 นาที

---

## 📋 สิ่งที่ต้องมี

- Windows 11
- RAM อย่างน้อย 8 GB
- พื้นที่ว่างอย่างน้อย 5 GB ถ้าไม่มีอย่าลองน้าาา!!
- อินเทอร์เน็ต

---

## 🐳 STEP 1 — ติดตั้ง Docker Desktop

### 1.1 ดาวน์โหลด

ไปที่ https://www.docker.com/products/docker-desktop แล้วกด **Download for Windows**

### 1.2 ติดตั้ง

เปิดไฟล์ `Docker Desktop Installer.exe` แล้วทำตามขั้นตอน

> ⚠️ ถ้ามีถามว่า "Use WSL 2 instead of Hyper-V" → ติ๊กถูกไว้

### 1.3 Restart

หลังติดตั้งเสร็จ Windows จะขอ restart — กด Restart ได้เลย

### 1.4 เปิด Docker Desktop

หลัง restart เปิด Docker Desktop จาก Start Menu รอจนไอคอน 🐳 ใน taskbar หยุดหมุน แล้วขึ้นว่า **"Docker Desktop is running"**

### 1.5 ตรวจสอบ

เปิด PowerShell แล้วรัน:

```powershell
docker --version
docker-compose --version
```

ควรได้ผลประมาณนี้:
```
Docker version 24.x.x
Docker Compose version v2.x.x
```

---

## 🐍 STEP 2 — ติดตั้ง Python

> ถ้ามี Python 3.9+ อยู่แล้ว ข้ามขั้นตอนนี้ได้เลย

### 2.1 ดาวน์โหลด

ไปที่ https://www.python.org/downloads แล้วกด **Download Python 3.11.x**

### 2.2 ติดตั้ง

เปิดไฟล์ติดตั้ง แล้ว **ติ๊กถูกที่ "Add Python to PATH"** ก่อนกด Install

```
☑️ Add Python 3.11 to PATH   ← สำคัญมาก! ต้องติ๊กก่อน
```

### 2.3 ตรวจสอบ

เปิด PowerShell ใหม่แล้วรัน:

```powershell
python --version
pip --version
```

---

## 📂 STEP 3 — เปิดโปรเจกต์

### 3.1 รับไฟล์โปรเจกต์

**วิธีที่ 1 — ถ้ามี Git:**
```powershell
git clone <repo-url>
cd mountain-network
```

**วิธีที่ 2 — ถ้าได้ไฟล์ ZIP มา:**
1. แตกไฟล์ ZIP
2. เปิด PowerShell
3. `cd` ไปที่โฟลเดอร์ที่แตกออกมา เช่น:
```powershell
cd C:\Users\YourName\Downloads\mountain-network
```

### 3.2 ตรวจสอบว่าอยู่ถูกโฟลเดอร์

```powershell
ls
```

ควรเห็น:
```
docker-compose.yml
monitor.py
demo_v2.py
node/
```

---

## 📦 STEP 4 — ติดตั้ง Python Libraries

```powershell
pip install httpx
```

---

## 🚀 STEP 5 — รัน Mountain Network

### 5.1 Build และรัน (ครั้งแรกใช้เวลา 3-5 นาที)

```powershell
docker-compose up -d --build
```

รอจนเห็นข้อความแบบนี้:
```
✔ Container internet-gateway  Started
✔ Container summit-alpha       Started
✔ Container village-a          Started
...
```

### 5.2 เช็คว่า containers รันครบ

```powershell
docker ps
```

ควรเห็น 13 containers ที่ status `Up`

### 5.3 ทดสอบเบื้องต้น

เปิด browser แล้วไปที่ http://localhost:9001/health

ควรเห็น:
```json
{"node":"village-a","role":"village","status":"online",...}
```

---

## 🎬 STEP 6 — รัน Demo

```powershell
python demo_v2.py
```

กด **Enter** เพื่อเดินหน้าแต่ละขั้นตอน — script จะแสดงผล PASS/FAIL อัตโนมัติ

---

## 🤖 รัน AI Monitor (Optional)

เปิด PowerShell อีกหน้าต่างหนึ่ง แล้วรัน:

```powershell
python monitor.py
```

จะอัปเดตทุก 20 วินาที กด `Ctrl+C` เพื่อหยุด

---

## 🛑 หยุด Network

```powershell
docker-compose down
```

---

## 🔧 Troubleshoot ปัญหาที่เจอบ่อย

### ❌ "docker: command not found"

Docker Desktop ยังไม่ได้เปิด หรือติดตั้งไม่สำเร็จ

แก้: เปิด Docker Desktop จาก Start Menu รอให้ไอคอนหยุดหมุนก่อน แล้วลองใหม่

---

### ❌ "port is already in use"

Port 9000-9006 ถูกใช้งานอยู่แล้ว

แก้:
```powershell
# หา process ที่ใช้ port อยู่
netstat -ano | findstr :9001

# ปิด process (แทน PID ด้วยเลขที่เห็น)
taskkill /PID <PID> /F
```

---

### ❌ "WSL 2 installation is incomplete"

ต้องอัปเดต WSL2 kernel ก่อน

แก้: เปิด PowerShell แบบ **Run as Administrator** แล้วรัน:
```powershell
wsl --update
```
แล้ว restart Docker Desktop

---

### ❌ demo.py รันแล้ว error "ModuleNotFoundError: No module named 'httpx'"

ยังไม่ได้ติดตั้ง library

แก้:
```powershell
pip install httpx
```

---

### ❌ Health check ได้ `{"error": "..."}`

Container ยังไม่พร้อม รอสักครู่แล้วลองใหม่ หรือเช็ค logs:

```powershell
docker-compose logs village-a
```

---

### ❌ docker-compose build นานมาก หรือค้าง

อาจเป็นเพราะ download image ช้า ลองรัน:
```powershell
# ล้าง cache แล้ว build ใหม่
docker-compose down
docker system prune -f
docker-compose up -d --build
```

---

## 📞 ถ้าแก้ไม่ได้ คำแนะนำจาก Claude.AI

ส่ง screenshot ของ error มาให้ทีม DevOps ดูครับ พร้อมบอกว่า:
1. รันคำสั่งอะไรอยู่
2. เห็น error ข้อความว่าอะไร
3. Windows version อะไร (กด `Win + R` พิมพ์ `winver`)
