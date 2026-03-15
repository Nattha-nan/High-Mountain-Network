#############################################################################
# HIGH MOUNTAIN NETWORK - MANAGEMENT COMMANDS FOR WINDOWS 11 (PowerShell)
# ไฟล์รวมคำสั่งทั้งหมดสำหรับจัดการระบบเครือข่ายจำลอง
# วิธีใช้: คัดลอกและวางคำสั่งที่ต้องการทีละบรรทัด หรือรันทั้งไฟล์
#############################################################################

# ===========================================================================
# ส่วนที่ 1: DOCKER MANAGEMENT - การจัดการ Docker containers
# ===========================================================================

Write-Host "`n=== DOCKER MANAGEMENT COMMANDS ===" -ForegroundColor Cyan

# รัน containers ครั้งแรก (build และรัน)
Write-Host "`n[รันครั้งแรก] docker-compose up -d --build" -ForegroundColor Yellow
docker-compose up -d --build

# รัน containers โดยไม่ build ใหม่
Write-Host "`n[รันปกติ] docker-compose up -d" -ForegroundColor Yellow
docker-compose up -d

# หยุดและลบ containers ทั้งหมด
Write-Host "`n[หยุดและลบ] docker-compose down" -ForegroundColor Yellow
docker-compose down

# หยุด containers โดยไม่ลบ
Write-Host "`n[หยุดชั่วคราว] docker-compose stop" -ForegroundColor Yellow
docker-compose stop

# รัน containers ที่หยุดไว้
Write-Host "`n[เริ่มใหม่] docker-compose start" -ForegroundColor Yellow
docker-compose start

# รีสตาร์ท containers ทั้งหมด
Write-Host "`n[รีสตาร์ท] docker-compose restart" -ForegroundColor Yellow
docker-compose restart

# ดู containers ที่กำลังรันอยู่
Write-Host "`n[ดู containers ที่รัน] docker ps" -ForegroundColor Yellow
docker ps

# ดู containers แบบกระชับ (เฉพาะชื่อและสถานะ)
Write-Host "`n[ดู containers แบบกระชับ]" -ForegroundColor Yellow
docker ps --format "table {{.Names}}\t{{.Status}}"

# ดู containers ทั้งหมด (รวมที่หยุดแล้ว)
Write-Host "`n[ดู containers ทั้งหมด]" -ForegroundColor Yellow
docker ps -a

# ดู logs ของ container แต่ละตัว
Write-Host "`n[ดู logs] docker logs [container_name]" -ForegroundColor Yellow
# docker logs village-a
# docker logs relay-center
# docker logs summit-alpha

# ===========================================================================
# ส่วนที่ 2: NETWORK MANAGEMENT - การจัดการเครือข่าย
# ===========================================================================

Write-Host "`n=== NETWORK MANAGEMENT COMMANDS ===" -ForegroundColor Cyan

# ดู networks ทั้งหมด
Write-Host "`n[ดู networks] docker network ls" -ForegroundColor Yellow
docker network ls

# ดูรายละเอียด network แต่ละตัว
Write-Host "`n[ดูรายละเอียด network]" -ForegroundColor Yellow
# docker network inspect mountain-network_access_net_north
# docker network inspect mountain-network_access_net_south

# ตัดการเชื่อมต่อ network (จำลองลิงก์ขาด)
Write-Host "`n[ตัดการเชื่อมต่อ - จำลองลิงก์ขาด]" -ForegroundColor Yellow
# ตัดเส้นเหนือ
docker network disconnect mountain-network_access_net_north relay-center
# ตัดเส้นใต้
docker network disconnect mountain-network_access_net_south relay-center

# เชื่อมต่อ network กลับคืน
Write-Host "`n[เชื่อมต่อกลับคืน]" -ForegroundColor Yellow
# ต่อเส้นเหนือ
docker network connect mountain-network_access_net_north relay-center
# ต่อเส้นใต้
docker network connect mountain-network_access_net_south relay-center

# ตัด 2 เส้นพร้อมกัน (ทดสอบ DTN - Delay Tolerant Network)
Write-Host "`n[ตัด 2 เส้นพร้อมกัน - DTN Test]" -ForegroundColor Yellow
docker network disconnect mountain-network_access_net_north relay-center
docker network disconnect mountain-network_access_net_south relay-center

# เช็คการเชื่อมต่อของ container
Write-Host "`n[เช็คการเชื่อมต่อ container]" -ForegroundColor Yellow
docker exec relay-center ping -c 3 relay-north

# ===========================================================================
# ส่วนที่ 3: HEALTH CHECK - ตรวจสอบสถานะของแต่ละ node
# ===========================================================================

Write-Host "`n=== HEALTH CHECK COMMANDS (PowerShell) ===" -ForegroundColor Cyan

# ฟังก์ชันช่วยสำหรับ Invoke-RestMethod
function Test-NodeHealth {
    param([int]$port, [string]$name)
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/health" -Method Get -TimeoutSec 2
        Write-Host "$name (port $port): $response" -ForegroundColor Green
    }
    catch {
        Write-Host "$name (port $port): ไม่สามารถเชื่อมต่อได้" -ForegroundColor Red
    }
}

# เช็คทีละ node (วิธีที่ 1: ใช้ฟังก์ชัน)
Write-Host "`n[เช็คสุขภาพ node ทีละตัว]" -ForegroundColor Yellow
Test-NodeHealth -port 9000 -name "internet-gateway"
Test-NodeHealth -port 9001 -name "village-a"
Test-NodeHealth -port 9002 -name "village-b"
Test-NodeHealth -port 9003 -name "village-c"
Test-NodeHealth -port 9004 -name "village-d"
Test-NodeHealth -port 9005 -name "sensor-cluster-1"
Test-NodeHealth -port 9006 -name "sensor-cluster-2"

# เช็คด้วย curl.exe (วิธีที่ 2: ใช้ curl.exe จริง)
Write-Host "`n[เช็คด้วย curl.exe]" -ForegroundColor Yellow
curl.exe -s http://localhost:9000/health
curl.exe -s http://localhost:9001/health
curl.exe -s http://localhost:9002/health

# ===========================================================================
# ส่วนที่ 4: SEND MESSAGES - การส่งข้อความระหว่าง nodes
# ===========================================================================

Write-Host "`n=== SEND MESSAGES COMMANDS (PowerShell) ===" -ForegroundColor Cyan

# ฟังก์ชันช่วยส่งข้อความ
function Send-Message {
    param([int]$port, [string]$origin, [string]$dest, [string]$content, [string]$priority)
    
    $body = @{
        origin = $origin
        destination = $dest
        content = $content
        priority = $priority
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/send" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body
        Write-Host "ส่งข้อความสำเร็จ: $response" -ForegroundColor Green
    }
    catch {
        Write-Host "ส่งข้อความล้มเหลว: $_" -ForegroundColor Red
    }
}

# ส่งข้อความ normal
Write-Host "`n[ส่งข้อความ normal]" -ForegroundColor Yellow
Send-Message -port 9001 -origin "village-a" -dest "relay-north" -content "Hello! สวัสดี" -priority "normal"

# ส่งข้อความ emergency
Write-Host "`n[ส่งข้อความ emergency]" -ForegroundColor Red
Send-Message -port 9002 -origin "village-b" -dest "relay-center" -content "EMERGENCY! ต้องการความช่วยเหลือ" -priority "emergency"

# ส่งข้อความ telemetry (ข้อมูลเซ็นเซอร์)
Write-Host "`n[ส่งข้อมูล telemetry]" -ForegroundColor Yellow
Send-Message -port 9005 -origin "sensor-cluster-1" -dest "village-a" -content "Temp: 42C, Humidity: 60%" -priority "telemetry"

# ส่งข้อความด้วย curl.exe (วิธีสำรอง)
Write-Host "`n[ส่งด้วย curl.exe]" -ForegroundColor Yellow
curl.exe -X POST http://localhost:9001/send `
  -H "Content-Type: application/json" `
  -d '{\"origin\":\"village-a\",\"destination\":\"relay-north\",\"content\":\"Hello via curl\",\"priority\":\"normal\"}'

# ===========================================================================
# ส่วนที่ 5: VIEW QUEUE & LOG - ดูคิวข้อความและ logs
# ===========================================================================

Write-Host "`n=== VIEW QUEUE & LOG COMMANDS ===" -ForegroundColor Cyan

# ฟังก์ชันดู queue
function Get-Queue {
    param([int]$port, [string]$name)
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/queue" -Method Get
        Write-Host "`nQueue ของ $name (port $port):" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    }
    catch {
        Write-Host "$name: ไม่สามารถดู queue ได้" -ForegroundColor Red
    }
}

# ฟังก์ชันดู log
function Get-Log {
    param([int]$port, [string]$name)
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/log" -Method Get
        Write-Host "`nLog ของ $name (port $port):" -ForegroundColor Green
        $response | ConvertTo-Json -Depth 3
    }
    catch {
        Write-Host "$name: ไม่สามารถดู log ได้" -ForegroundColor Red
    }
}

# ดู queue ของ nodes ที่มี port
Write-Host "`n[ดู queue ข้อความรอส่ง]" -ForegroundColor Yellow
Get-Queue -port 9001 -name "village-a"
Get-Queue -port 9002 -name "village-b"

# ดู log ของ nodes ที่มี port
Write-Host "`n[ดู log ข้อความที่รับแล้ว]" -ForegroundColor Yellow
Get-Log -port 9001 -name "village-a"
Get-Log -port 9002 -name "village-b"

# ดู log ของ nodes ที่ไม่มี port (relay, summit) ผ่าน docker exec
Write-Host "`n[ดู log relay-center ผ่าน docker exec]" -ForegroundColor Yellow
docker exec relay-center python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"

Write-Host "`n[ดู log relay-north ผ่าน docker exec]" -ForegroundColor Yellow
docker exec relay-north python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"

Write-Host "`n[ดู log summit-alpha ผ่าน docker exec]" -ForegroundColor Yellow
docker exec summit-alpha python3 -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/log').read().decode())"

# ===========================================================================
# ส่วนที่ 6: ENERGY / POWER MODE - การจัดการพลังงาน
# ===========================================================================

Write-Host "`n=== ENERGY / POWER MODE COMMANDS ===" -ForegroundColor Cyan

# ฟังก์ชันดูพลังงาน
function Get-Energy {
    param([int]$port, [string]$name)
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/energy" -Method Get
        Write-Host "$name พลังงาน: $response%" -ForegroundColor Yellow
    }
    catch {
        Write-Host "$name: ไม่สามารถดูพลังงานได้" -ForegroundColor Red
    }
}

# ฟังก์ชันตั้งค่าพลังงาน
function Set-Energy {
    param([int]$port, [int]$level)
    $body = @{ level = $level } | ConvertTo-Json
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/energy" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body
        Write-Host "ตั้งค่าพลังงานที่ $level% สำเร็จ" -ForegroundColor Green
    }
    catch {
        Write-Host "ตั้งค่าพลังงานล้มเหลว: $_" -ForegroundColor Red
    }
}

# ฟังก์ชันตั้งค่า low power mode
function Set-PowerMode {
    param([int]$port, [bool]$lowPower)
    $body = @{ low_power = $lowPower } | ConvertTo-Json
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:$port/power" `
            -Method Post `
            -ContentType "application/json" `
            -Body $body
        Write-Host "ตั้งค่า low power mode = $lowPower สำเร็จ" -ForegroundColor Green
    }
    catch {
        Write-Host "ตั้งค่า power mode ล้มเหลว: $_" -ForegroundColor Red
    }
}

# ดูพลังงานปัจจุบัน
Write-Host "`n[ดูพลังงานปัจจุบัน]" -ForegroundColor Yellow
Get-Energy -port 9001 -name "village-a"
Get-Energy -port 9002 -name "village-b"
Get-Energy -port 9005 -name "sensor-cluster-1"

# ลดพลังงาน (จำลองแบตเตอรี่ต่ำ)
Write-Host "`n[ลดพลังงานเหลือ 15%]" -ForegroundColor Yellow
Set-Energy -port 9002 -level 15

# เปิด Low Power Mode
Write-Host "`n[เปิด Low Power Mode]" -ForegroundColor Yellow
Set-PowerMode -port 9002 -lowPower $true

# คืนพลังงานกลับ
Write-Host "`n[คืนพลังงานเป็น 100%]" -ForegroundColor Yellow
Set-Energy -port 9002 -level 100

# ปิด Low Power Mode
Write-Host "`n[ปิด Low Power Mode]" -ForegroundColor Yellow
Set-PowerMode -port 9002 -lowPower $false

# ===========================================================================
# ส่วนที่ 7: MONITORING - การตรวจสอบระบบอัตโนมัติ
# ===========================================================================

Write-Host "`n=== MONITORING COMMANDS ===" -ForegroundColor Cyan

# รัน AI monitor (อัปเดตทุก 20 วินาที)
Write-Host "`n[รัน AI Monitor] python monitor.py" -ForegroundColor Yellow
# python monitor.py

# รัน demo script
Write-Host "`n[รัน Demo Script] python demo_v2.py" -ForegroundColor Yellow
# python demo_v2.py

# สคริปต์มอนิเตอร์แบบง่าย
Write-Host "`n[มอนิเตอร์แบบง่าย]" -ForegroundColor Yellow
while ($true) {
    Clear-Host
    Write-Host "=== HIGH MOUNTAIN NETWORK MONITOR ===" -ForegroundColor Cyan
    Write-Host "เวลา: $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Yellow
    
    # เช็ค containers
    docker ps --format "table {{.Names}}\t{{.Status}}"
    
    Write-Host "`nกด Ctrl+C เพื่อหยุด" -ForegroundColor Red
    Start-Sleep -Seconds 5
}

# ===========================================================================
# ส่วนที่ 8: TROUBLESHOOTING - การแก้ไขปัญหา
# ===========================================================================

Write-Host "`n=== TROUBLESHOOTING COMMANDS ===" -ForegroundColor Cyan

# เช็ค port ที่ใช้อยู่
Write-Host "`n[เช็ค port 9000-9006]" -ForegroundColor Yellow
netstat -ano | findstr ":900[0-6]"

# ดูรายละเอียด process ที่ใช้ port
Write-Host "`n[ดู process ที่ใช้ port]" -ForegroundColor Yellow
$ports = @(9000,9001,9002,9003,9004,9005,9006)
foreach ($port in $ports) {
    $process = netstat -ano | findstr ":$port"
    if ($process) {
        Write-Host "Port $port: ถูกใช้งาน" -ForegroundColor Yellow
        $process
    } else {
        Write-Host "Port $port: ว่าง" -ForegroundColor Green
    }
}

# ล้าง network ที่ค้าง
Write-Host "`n[ล้าง network ที่ไม่ใช้งาน]" -ForegroundColor Yellow
docker network prune -f

# ดู logs ของ containers ที่มีปัญหา
Write-Host "`n[ดู logs containers]" -ForegroundColor Yellow
# docker logs relay-center --tail 50
# docker logs summit-alpha --tail 50
# docker logs village-a --tail 50

# รีสตาร์ทเฉพาะ container
Write-Host "`n[รีสตาร์ทเฉพาะ container]" -ForegroundColor Yellow
# docker restart relay-center
# docker restart village-a

# เข้าไปใน container เพื่อ debug
Write-Host "`n[เข้าไปใน container]" -ForegroundColor Yellow
# docker exec -it relay-center /bin/sh
# docker exec -it village-a /bin/sh

# ===========================================================================
# ส่วนที่ 9: BATCH OPERATIONS - การทำงานแบบกลุ่ม
# ===========================================================================

Write-Host "`n=== BATCH OPERATIONS ===" -ForegroundColor Cyan

# รีสตาร์ททั้งหมดและทดสอบ
function Restart-And-Test {
    Write-Host "1. รีสตาร์ท containers..." -ForegroundColor Yellow
    docker-compose restart
    
    Write-Host "2. รอ 5 วินาที..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host "3. ทดสอบส่งข้อความ..." -ForegroundColor Yellow
    Send-Message -port 9001 -origin "village-a" -dest "relay-north" -content "Test after restart" -priority "normal"
    
    Write-Host "4. ดู logs..." -ForegroundColor Yellow
    Get-Log -port 9001 -name "village-a"
}

# ทดสอบ DTN (ตัดการเชื่อมต่อ)
function Test-DTN {
    Write-Host "1. ตัดการเชื่อมต่อ relay-center" -ForegroundColor Red
    docker network disconnect mountain-network_access_net_north relay-center
    docker network disconnect mountain-network_access_net_south relay-center
    
    Write-Host "2. ส่งข้อความ (ควรค้างใน queue)" -ForegroundColor Yellow
    Send-Message -port 9001 -origin "village-a" -dest "relay-center" -content "DTN Test" -priority "normal"
    
    Write-Host "3. ดู queue" -ForegroundColor Yellow
    Get-Queue -port 9001 -name "village-a"
    
    Write-Host "4. รอ 10 วินาที..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host "5. เชื่อมต่อกลับ" -ForegroundColor Green
    docker network connect mountain-network_access_net_north relay-center
    docker network connect mountain-network_access_net_south relay-center
    
    Write-Host "6. รอ 5 วินาที..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host "7. ดู log ว่าข้อความส่งสำเร็จหรือไม่" -ForegroundColor Yellow
    Get-Log -port 9001 -name "village-a"
}

# ===========================================================================
# ส่วนที่ 10: QUICK REFERENCES - ตารางอ้างอิงด่วน
# ===========================================================================

Write-Host "`n=== QUICK REFERENCE ===" -ForegroundColor Cyan
Write-Host @"
PORT MAPPING:
------------
9000 - internet-gateway (เชื่อมต่ออินเทอร์เน็ต)
9001 - village-a (หมู่บ้าน A)
9002 - village-b (หมู่บ้าน B)
9003 - village-c (หมู่บ้าน C)
9004 - village-d (หมู่บ้าน D)
9005 - sensor-cluster-1 (เซ็นเซอร์กลุ่ม 1)
9006 - sensor-cluster-2 (เซ็นเซอร์กลุ่ม 2)

RELAY NODES (เข้า via docker exec เท่านั้น):
----------
relay-north, relay-center, relay-east
summit-alpha, summit-beta, summit-gamma

NETWORK NAMES:
-------------
mountain-network_access_net_north
mountain-network_access_net_south
mountain-network_backbone_net

PRIORITY LEVELS:
---------------
normal, emergency, telemetry

ENERGY LEVELS:
-------------
0-100% (ต่ำกว่า 20% จะเข้า low power mode)
"@ -ForegroundColor White

Write-Host "`n✅ รวมคำสั่งทั้งหมดสำหรับ Windows 11 พร้อมใช้งาน!" -ForegroundColor Green
Write-Host "📌 หมายเหตุ: บางคำสั่งต้องรันใน PowerShell เท่านั้น" -ForegroundColor Yellow