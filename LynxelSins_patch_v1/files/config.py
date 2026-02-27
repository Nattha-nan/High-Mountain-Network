"""
config.py — ค่าคงที่และการตั้งค่าทั้งหมดของโปรเจกต์
เหมือน Project Settings ใน Godot
"""

# ── หน้าจอ ──────────────────────────────────────────────────────────────
W, H       = 1600, 900
FPS        = 60
PANEL_W    = 600   # แผง UI ด้านขวา
BTN_BAR_H  = 48    # แถวปุ่มด้านล่าง

NET_W = W - PANEL_W   # พื้นที่แผนที่

# ── สี ──────────────────────────────────────────────────────────────────
BG           = (13,  17,  23)
PANEL_BG     = (22,  27,  34)
PANEL_BORDER = (33,  38,  45)

# สีโหนด
C_GATEWAY = (240, 136,  62)
C_BACKBONE = ( 88, 166, 255)
C_RELAY   = (188, 140, 255)
C_VILLAGE = ( 63, 185,  80)
C_IOT     = (118, 227, 234)

# สีลิงก์
C_LINK_OK   = ( 50, 120, 200)
C_LINK_FAIL = (180,  40,  40)
C_LINK_WEAK = (200, 160,  40)

# สี packet
C_PACKET     = (255, 220,  80)
C_PACKET_EMG = (255,  80,  80)
C_PACKET_DTN = (180, 100, 255)

# สี UI
C_TEXT     = (230, 237, 243)
C_MUTED    = (139, 148, 158)
C_GREEN    = ( 63, 185,  80)
C_RED      = (255,  68,  68)
C_YELLOW   = (227, 179,  65)
C_INPUT_BG = ( 30,  36,  44)
C_INPUT_BD = ( 88, 166, 255)
C_SEL      = (255, 220,  80)

# สีปุ่ม
C_BTN_BG     = ( 40,  50,  65)
C_BTN_HOVER  = ( 60,  80, 110)
C_BTN_BORDER = ( 80, 120, 180)
C_BTN_TEXT   = (200, 220, 255)

# ── ชนิดโหนด ──────────────────────────────────────────────────────────
NODE_COLOR = {
    "gateway": C_GATEWAY, "backbone": C_BACKBONE,
    "relay":   C_RELAY,   "village":  C_VILLAGE,  "iot": C_IOT
}
NODE_RADIUS = {
    "gateway": 22, "backbone": 19, "relay": 15, "village": 13, "iot": 10
}

# ── ชนิดลิงก์ ──────────────────────────────────────────────────────────
LINK_COLOR = {
    "fiber":     C_GATEWAY,
    "microwave": C_BACKBONE,
    "wifi":      C_VILLAGE,
    "lora":      C_IOT,
    "backup":    C_RELAY,
}

# ── ข้อมูลเครือข่าย ────────────────────────────────────────────────────
RAW_NODES = [
    ("GW", "Internet\nGateway",  0.50, 0.06, "gateway"),
    ("SA", "Summit\nAlpha",      0.22, 0.22, "backbone"),
    ("SB", "Summit\nBeta",       0.52, 0.20, "backbone"),
    ("SG", "Summit\nGamma",      0.78, 0.24, "backbone"),
    ("RN", "Relay\nNorth",       0.12, 0.44, "relay"),
    ("RC", "Relay\nCenter",      0.46, 0.46, "relay"),
    ("RE", "Relay\nEast",        0.82, 0.46, "relay"),
    ("VA", "Village\nA",         0.06, 0.68, "village"),
    ("VB", "Village\nB",         0.28, 0.72, "village"),
    ("VC", "Village\nC",         0.54, 0.74, "village"),
    ("VD", "Village\nD",         0.80, 0.70, "village"),
    ("S1", "Sensor\nCluster 1",  0.16, 0.90, "iot"),
    ("S2", "Sensor\nCluster 2",  0.66, 0.90, "iot"),
]

RAW_LINKS = [
    ("GW","SA",  300, "fiber"),
    ("GW","SB",  200, "microwave"),
    ("SA","SB",  150, "microwave"),
    ("SB","SG",  120, "microwave"),
    ("SA","RN",   80, "wifi"),
    ("SB","RC",   90, "wifi"),
    ("SG","RE",   70, "wifi"),
    ("RN","VA",   30, "wifi"),
    ("RN","VB",   35, "wifi"),
    ("RC","VB",   25, "wifi"),
    ("RC","VC",   40, "wifi"),
    ("RE","VC",   30, "wifi"),
    ("RE","VD",   28, "wifi"),
    ("VA","S1",   10, "lora"),
    ("VD","S2",   10, "lora"),
    ("SA","RC",   60, "backup"),
    ("SG","RC",   55, "backup"),
    ("VB","VC",   20, "backup"),
]
