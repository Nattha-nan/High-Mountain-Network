"""
packets.py — Packet class
เหมือน "กระสุน" หรือ "อนุภาค" ใน Godot (AnimatedSprite/GPUParticles)
ทำหน้าที่: เคลื่อนที่ตาม path, วาด trail, ตรวจว่าถึงปลายทางแล้ว
"""

from collections import deque
import pygame

from config import C_PACKET, C_PACKET_EMG, C_PACKET_DTN


class Packet:
    """
    Packet ที่เดินทางผ่านเครือข่าย
    - normal    → สีเหลือง, drop ทันทีถ้าลิงก์ขาด
    - emergency → สีแดง, รอใน DTN buffer
    - dtn       → สีม่วง, รอใน DTN buffer เสมอ
    """

    RADIUS = 6

    def __init__(self, msg, path, ptype="normal"):
        self.msg      = msg
        self.path     = path     # list ของ Node objects
        self.ptype    = ptype

        self.seg      = 0        # index segment ปัจจุบัน
        self.progress = 0.0      # 0.0 → 1.0 ระหว่างสอง node
        self.speed    = 0.004 if ptype == "dtn" else 0.006

        self.done     = False    # ถึงปลายทางแล้ว
        self.dead     = False    # โดน drop (ลบออกจาก list)
        self.buffered = False    # รอใน DTN buffer อยู่

        self.trail = deque(maxlen=12)   # ประวัติตำแหน่ง (วาด tail)

    # ── สี ────────────────────────────────────────────────────────────
    @property
    def color(self):
        return {
            "normal":    C_PACKET,
            "emergency": C_PACKET_EMG,
            "dtn":       C_PACKET_DTN,
        }.get(self.ptype, C_PACKET)

    # ── ตำแหน่งปัจจุบัน (interpolate ระหว่าง node) ───────────────────
    @property
    def pos(self):
        if self.seg >= len(self.path) - 1:
            return (self.path[-1].x, self.path[-1].y)
        n1 = self.path[self.seg]
        n2 = self.path[self.seg + 1]
        x  = n1.x + (n2.x - n1.x) * self.progress
        y  = n1.y + (n2.y - n1.y) * self.progress
        return (int(x), int(y))

    # ── update ทุก frame ──────────────────────────────────────────────
    def update(self, link_map):
        if self.done or self.dead or self.buffered:
            return
        if self.seg >= len(self.path) - 1:
            self.done = True
            return

        n1  = self.path[self.seg]
        n2  = self.path[self.seg + 1]
        key = (n1.id, n2.id)
        lnk = link_map.get(key) or link_map.get((n2.id, n1.id))

        # ตรวจสอบลิงก์
        if lnk and not lnk.alive:
            if self.ptype in ["dtn", "emergency"]:
                n1.buffer.append(self)
                self.buffered = True   # หยุดรอ (ไม่ถูกลบ)
            else:
                self.dead = True       # drop
            return

        # เคลื่อนที่
        self.trail.append(self.pos)
        self.progress += self.speed * (lnk.quality if lnk else 1.0)
        if self.progress >= 1.0:
            self.progress = 0.0
            self.seg += 1

    # ── วาด ───────────────────────────────────────────────────────────
    def draw(self, surf):
        if self.done or self.dead or self.buffered:
            return

        # วาด trail (จางออกจากหัว)
        for i, (tx, ty) in enumerate(self.trail):
            alpha = int(180 * i / max(1, len(self.trail)))
            r = max(1, self.RADIUS - 3)
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (r, r), r)
            surf.blit(s, (tx - r, ty - r))

        # วาดหัว packet
        x, y = self.pos
        pygame.draw.circle(surf, (0, 0, 0), (x+1, y+1), self.RADIUS)
        pygame.draw.circle(surf, self.color,       (x, y), self.RADIUS)
        pygame.draw.circle(surf, (255, 255, 255),  (x, y), self.RADIUS, 1)
