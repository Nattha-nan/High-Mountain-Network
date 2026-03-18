นี่คือ Cheat Sheet ที่ปรับให้ใช้กับ **Windows 11 + PowerShell + Docker Compose** 
---
# 🏔️ High-Mountain-Network Command Cheat Sheet for Windows 11

## 📦 Docker Management (PowerShell)

```powershell
# รัน / หยุด
docker-compose up -d --build    # build และรันครั้งแรก
docker-compose up -d            # รันโดยไม่ build ใหม่
docker-compose down             # หยุดและลบ containers

# เช็คสถานะ
docker ps                                              # ดู containers ที่รันอยู่
docker ps --format "table {{.Names}}\t{{.Status}}"    # แบบกระชับ
docker logs village-a                                  # ดู log ของ container
```

## 🌐 Network Commands

```powershell
# ตัด/ต่อลิงก์ (จำลองลิงก์ขาด)
docker network disconnect mountain-network_access_net_north relay-center
docker network connect mountain-network_access_net_north relay-center

# ตัด 2 เส้น (DTN test)
docker network disconnect mountain-network_access_net_north relay-center
docker network disconnect mountain-network_access_net_south relay-center

# ดู networks ทั้งหมด
docker network ls
```

## ❤️ Health Check (ใช้ curl.exe ใน PowerShell)

```powershell
# เช็คทีละ node
curl.exe http://localhost:9000/health    # internet-gateway
curl.exe http://localhost:9001/health    # village-a
curl.exe http://localhost:9002/health    # village-b
curl.exe http://localhost:9003/health    # village-c
curl.exe http://localhost:9004/health    # village-d
curl.exe http://localhost:9005/health    # sensor-cluster-1
curl.exe http://localhost:9006/health    # sensor-cluster-2
```

## 📨 Send Messages (PowerShell)

```powershell
# ส่ง normal (ใช้ Invoke-RestMethod)
Invoke-RestMethod -Uri "http://localhost:9001/send" `
-Method Post `
-ContentType "application/json" `
-Body '{"origin":"village-a","destination":"village-b","content":"Hello","priority":"normal"}'

# ส่ง emergency
Invoke-RestMethod -Uri "http://localhost:9002/send" `
-Method Post `
-ContentType "application/json" `
-Body '{"origin":"village-b","destination":"relay-center","content":"EMERGENCY! Flood detected!","priority":"emergency"}'

# ส่ง telemetry
Invoke-RestMethod -Uri "http://localhost:9005/send" `
-Method Post `
-ContentType "application/json" `
-Body '{"origin":"sensor-cluster-1","destination":"village-a","content":"Temp: 42C","priority":"telemetry"}'


## 📊 ดู Log / Queue

```powershell
# ดู queue (ข้อความรอส่ง)
curl.exe http://localhost:9002/queue

# ดู log (ข้อความที่รับแล้ว) — เฉพาะ node ที่มี port expose
curl.exe http://localhost:9001/log
curl.exe http://localhost:9002/log

# ดู log ของ node ที่ไม่มี port (relay, summit)
docker exec relay-center python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"
docker exec relay-north python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"
```

## 🔋 Energy / Power Mode

```powershell
# ดู energy ปัจจุบันInvoke-RestMethod -Uri "http://localhost:9002/energy"

# ลด energy (จำลองแบตต่ำ)
Invoke-RestMethod -Uri "http://localhost:9002/energy" `
-Method Post `
-ContentType "application/json" `
-Body '{"level": 15}'


# คืน energy กลับ
$body = '{"level": 100}'
Invoke-RestMethod -Uri "http://localhost:9002/energy" -Method POST -ContentType "application/json" -Body $body

# เปิด/ปิด low power mode ตรงๆ
Invoke-RestMethod -Uri "http://localhost:9002/energy" `
-Method Post `
-ContentType "application/json" `
-Body '{"level": 100}'


# ปิด low power mode
Invoke-RestMethod -Uri "http://localhost:9002/power" `
-Method Post `
-ContentType "application/json" `
-Body '{"low_power": true}'


## 📺 Monitor

```powershell
# รัน AI monitor (อัปเดตทุก 20 วินาที)
python monitor.py

# รัน demo script
python demo_v2.py
```

## 🔧 Troubleshoot

```powershell
# เช็ค port ที่ใช้อยู่
netstat -ano | findstr :9001

# ล้าง network ที่ค้าง
docker network prune -f

# ดู log ของ container ที่มีปัญหา
docker logs relay-center
docker logs summit-alpha

# restart container
docker-compose restart relay-center

# rebuild และรันใหม่ทั้งหมด
docker-compose down
docker-compose up -d --build
```

## 📝 PowerShell Tips

```powershell
# สร้าง function ช่วยส่ง message (ใส่ใน $PROFILE)
function Send-Message {
    param($Port, $Origin, $Dest, $Content, $Priority="normal")
    $body = @{
        origin = $Origin
        destination = $Dest
        content = $Content
        priority = $Priority
    } | ConvertTo-Json
    Invoke-RestMethod -Uri "http://localhost:$Port/send" -Method POST -ContentType "application/json" -Body $body
}

# ใช้:
Send-Message -Port 9001 -Origin "village-a" -Dest "relay-north" -Content "Hello!"
```

## ⚡ Quick Test All Nodes

```powershell
# สร้าง test script
@"
Write-Host "Testing all nodes..." -ForegroundColor Green
9000..9006 | ForEach-Object {
    try {
        $result = curl.exe -s "http://localhost:$_/health"
        Write-Host "Node $_ : OK" -ForegroundColor Green
    } catch {
        Write-Host "Node $_ : Failed" -ForegroundColor Red
    }
}
"@ | Out-File -FilePath test-nodes.ps1

# รัน
.\test-nodes.ps1
```

---

**ข้อสังเกตสำคัญ:**
- ใช้ `curl.exe` แทน `curl` ใน PowerShell (เพราะ curl ใน PowerShell คือ alias ของ Invoke-WebRequest)
- หรือใช้ `Invoke-RestMethod` ซึ่งจัดการ JSON ได้ดีกว่า
- เว้นวรรคหลัง `\` ใน PowerShell เพื่อตัดบรรทัด
- ใช้ `python` แทน `python3` ใน Windows
