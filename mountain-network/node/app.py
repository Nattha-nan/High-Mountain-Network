import os, asyncio, httpx
from datetime import datetime
from fastapi import FastAPI
from pydantic import BaseModel
from contextlib import asynccontextmanager

# DTN Queue — เก็บข้อความที่ส่งไม่ได้
dtn_queue = []
message_log = []
low_power_mode = False
energy_level = 100

NODE_NAME = os.getenv("NODE_NAME", "unknown")
NODE_ROLE = os.getenv("NODE_ROLE", "village")
NEIGHBORS = os.getenv("NEIGHBORS", "").split(",")

class Message(BaseModel):
    origin: str
    destination: str
    content: str
    priority: str = "normal"
    timestamp: str = ""

async def retry_loop():
    """DTN retry — ลองส่งซ้ำทุก 30 วินาที เรียงตาม priority"""
    priority_order = {"emergency": 0, "telemetry": 1, "normal": 2}
    while True:
        await asyncio.sleep(30)
        failed = []
        
        #  เรียง queue ตาม priority ก่อนส่ง
        sorted_queue = sorted(
            dtn_queue,
            key=lambda m: priority_order.get(m.get("priority", "normal"), 2)
        )
        
        for msg_dict in sorted_queue:
            msg = Message(**msg_dict)
            url = f"http://{msg.destination}:8000/receive"
            try:
                async with httpx.AsyncClient(timeout=3.0) as client:
                    await client.post(url, json=msg_dict)
                print(f"[QoS] Delivered [{msg.priority}] → {msg.destination}")
            except:
                failed.append(msg_dict)
        dtn_queue.clear()
        dtn_queue.extend(failed)

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(retry_loop())  # ← เริ่ม retry loop ตอน startup
    yield                               # ← app รันอยู่ตรงนี้
                                        # ← ถ้ามี cleanup ใส่หลัง yield

app = FastAPI(lifespan=lifespan)        # ← ผูก lifespan กับ app

@app.get("/health")
def health():
    return {
        "node": NODE_NAME,
        "role": NODE_ROLE,
        "neighbors": NEIGHBORS,
        "queue_size": len(dtn_queue),
        "status": "online",
        "energy_level": energy_level,        # ← เพิ่ม
        "low_power_mode": low_power_mode      # ← เพิ่ม
    }

@app.post("/send")
async def send_message(msg: Message):
    msg.timestamp = datetime.now().isoformat()
    msg.origin = NODE_NAME
    result = await try_deliver(msg)
    return result

@app.post("/receive")
async def receive_message(msg: Message):
    # Low power mode — ปฏิเสธ traffic ที่ไม่จำเป็น
    if low_power_mode and msg.priority in ["normal", "telemetry"]:
        return {
            "status": "rejected",
            "reason": "low power mode — only emergency traffic accepted",
            "node": NODE_NAME
        }
    message_log.append(msg.model_dump())
    return {"status": "received", "node": NODE_NAME, "message": msg.content}

@app.get("/log")
def get_log():
    return {"node": NODE_NAME, "messages": message_log}

@app.get("/queue")
def get_queue():
    return {"node": NODE_NAME, "queued": dtn_queue}

@app.post("/power")
async def set_power_mode(mode: dict):
    global low_power_mode
    low_power_mode = mode.get("low_power", False)
    return {
        "node": NODE_NAME,
        "low_power_mode": low_power_mode,
        "message": "Low power mode ON — best-effort traffic disabled" if low_power_mode else "Normal mode restored"
    }

@app.get("/power")
def get_power_mode():
    return {"node": NODE_NAME, "low_power_mode": low_power_mode}

async def try_deliver(msg: Message):
    target = None
    for n in NEIGHBORS:
        if n.strip() == msg.destination:
            target = n.strip()
            break

    if not target:
        dtn_queue.append(msg.model_dump())
        return {"status": "queued", "reason": "destination not in neighbors"}

    url = f"http://{target}:8000/receive"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.post(url, json=msg.model_dump())
            result = response.json()
            # เช็ค response จาก receiver
            if result.get("status") == "rejected":
                return {
                    "status": "rejected",
                    "reason": result.get("reason"),
                    "to": target
                }
        return {"status": "delivered", "to": target}
    except Exception as e:
        dtn_queue.append(msg.model_dump())
        return {"status": "queued", "reason": str(e)}
    
@app.post("/energy")
async def set_energy(data: dict):
    global energy_level, low_power_mode
    energy_level = max(0, min(100, data.get("level", 100)))
    # ถ้าพลังงานต่ำกว่า 20% → เข้า low power อัตโนมัติ
    if energy_level < 20:
        low_power_mode = True
        msg = f"⚠️ Low energy ({energy_level}%) — auto low power mode ON"
    elif energy_level >= 50:
        low_power_mode = False
        msg = f"✅ Energy restored ({energy_level}%) — normal mode"
    else:
        msg = f"Energy at {energy_level}% — monitoring"
    return {"node": NODE_NAME, "energy_level": energy_level, "low_power_mode": low_power_mode, "message": msg}

@app.get("/energy")
def get_energy():
    return {"node": NODE_NAME, "energy_level": energy_level, "low_power_mode": low_power_mode}