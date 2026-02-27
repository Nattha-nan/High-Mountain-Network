"""
links.py — Link class
เหมือน script ของ "เส้นเชื่อม" ใน Godot
ทำหน้าที่: เก็บสถานะลิงก์, วาดเส้น (รองรับเส้นประ), จำลอง flicker
"""

import math
import random
import pygame

from config import (
    C_LINK_OK, C_LINK_FAIL, C_LINK_WEAK, LINK_COLOR
)


class Link:
    """
    ลิงก์ระหว่างโหนด 2 โหนด
    alive = False → สัญญาณขาด (แสดงเป็นสีแดง)
    quality < 0.5 → สัญญาณอ่อน (สีเหลือง)
    """

    def __init__(self, src_node, dst_node, bandwidth, link_type):
        self.src     = src_node
        self.dst     = dst_node
        self.bw      = bandwidth
        self.type    = link_type
        self.alive   = True
        self.quality = 1.0
        self.backup  = (link_type == "backup")
        self.flicker_timer = 0.0   # นับถอยหลังก่อนกลับมา alive

    # ── สี / ความหนา ──────────────────────────────────────────────────
    def color(self):
        if not self.alive:
            return C_LINK_FAIL
        if self.quality < 0.5:
            return C_LINK_WEAK
        return LINK_COLOR.get(self.type, C_LINK_OK)

    def width(self):
        if self.backup:
            return 1
        return max(1, int(self.bw / 60))

    # ── toggle on/off ─────────────────────────────────────────────────
    def toggle(self):
        self.alive = not self.alive

    # ── update ทุก frame ──────────────────────────────────────────────
    def update(self, dt):
        # เปลี่ยน quality แบบ random walk
        self.quality += random.uniform(-0.02, 0.02)
        self.quality  = max(0.1, min(1.0, self.quality))

        # นับถอยหลัง flicker timer
        if self.flicker_timer > 0:
            self.flicker_timer -= dt
            if self.flicker_timer <= 0:
                self.alive   = True
                self.quality = 1.0

    # ── วาด ───────────────────────────────────────────────────────────
    def draw(self, surf):
        n1, n2 = self.src, self.dst
        col    = self.color()

        if self.backup:
            # วาดเส้นประสำหรับ backup link
            dx   = n2.x - n1.x
            dy   = n2.y - n1.y
            dist = max(1, math.hypot(dx, dy))
            dash, step = 8, 16
            for i in range(0, int(dist), step):
                t0 = i / dist
                t1 = min((i + dash) / dist, 1.0)
                x0 = int(n1.x + dx * t0);  y0 = int(n1.y + dy * t0)
                x1 = int(n1.x + dx * t1);  y1 = int(n1.y + dy * t1)
                pygame.draw.line(surf, col, (x0, y0), (x1, y1), 1)
        else:
            pygame.draw.line(surf, col, (n1.x, n1.y), (n2.x, n2.y), self.width())
