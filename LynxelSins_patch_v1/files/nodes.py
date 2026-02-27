"""
nodes.py — Node class
เหมือน Node script ใน Godot  (เช่น CharacterBody2D.gd)
ทำหน้าที่: วาดตัวเอง, ตรวจ click, เก็บ DTN buffer
"""

import math
import time
from collections import deque
import pygame

from config import (
    NODE_COLOR, NODE_RADIUS,
    C_TEXT, C_SEL, C_PACKET_DTN, C_PACKET_EMG, C_PACKET,
    NET_W, H
)


class Node:
    """
    โหนดในเครือข่าย — เปรียบได้กับ Node ใน Godot
    แต่ละโหนดรู้จักตัวเองและวาดตัวเองได้ (draw)
    """

    def __init__(self, nid, label, rx, ry, ntype):
        self.id     = nid
        self.label  = label
        # แปลงพิกัดสัดส่วน → pixel
        self.x      = int(rx * NET_W)
        self.y      = int(ry * (H - 80)) + 40
        self.type   = ntype
        self.color  = NODE_COLOR[ntype]
        self.radius = NODE_RADIUS[ntype]

        self.buffer  = deque(maxlen=20)   # DTN store-and-forward buffer
        self.pulse   = 0.0                # animation counter
        self.last_flush_attempt = 0.0

    # ── วาด ───────────────────────────────────────────────────────────
    def draw(self, surf, font_xs, selected: bool):
        # วงแสงเมื่อถูกเลือก
        if selected:
            glow_r = self.radius + 8
            s = pygame.Surface((glow_r*2+4, glow_r*2+4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*C_SEL, 60), (glow_r+2, glow_r+2), glow_r)
            surf.blit(s, (self.x - glow_r - 2, self.y - glow_r - 2))

        # วงกระพริบเมื่อมี DTN buffer
        if self.buffer:
            pr = self.radius + 4 + int(4 * abs(math.sin(self.pulse)))
            pygame.draw.circle(surf, C_PACKET_DTN, (self.x, self.y), pr, 2)

        # เงา + ตัวโหนด + ขอบ
        pygame.draw.circle(surf, (0, 0, 0), (self.x+2, self.y+2), self.radius)
        pygame.draw.circle(surf, self.color,   (self.x, self.y),   self.radius)
        border_col = C_SEL if selected else (200, 200, 200)
        pygame.draw.circle(surf, border_col, (self.x, self.y), self.radius, 2)

        # ชื่อโหนด (วาดทีละบรรทัด)
        for i, line in enumerate(self.label.split("\n")):
            txt = font_xs.render(line, True, C_TEXT)
            surf.blit(txt, (
                self.x - txt.get_width() // 2,
                self.y + self.radius + 2 + i * 11
            ))

        # badge แสดงจำนวน packet ใน buffer
        if self.buffer:
            badge = font_xs.render(f"▣{len(self.buffer)}", True, C_PACKET_DTN)
            surf.blit(badge, (
                self.x - badge.get_width() // 2,
                self.y - self.radius - 13
            ))

    # ── ตรวจ click ────────────────────────────────────────────────────
    def hit(self, mx, my) -> bool:
        return math.hypot(mx - self.x, my - self.y) <= self.radius + 6

    # ── หา path (BFS บน alive links) ─────────────────────────────────
    def find_path_to(self, dst_id, link_map, nodes_dict):
        visited = {self.id}
        queue   = deque([[self.id]])
        adj     = {}
        for (a, b), lnk in link_map.items():
            if lnk.alive:
                adj.setdefault(a, []).append(b)
                adj.setdefault(b, []).append(a)

        while queue:
            path = queue.popleft()
            cur  = path[-1]
            if cur == dst_id:
                return [nodes_dict[n] for n in path if n in nodes_dict]
            for nxt in adj.get(cur, []):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(path + [nxt])
        return None

    # ── DTN flush: ส่ง packet ที่รอออกไปเมื่อลิงก์กลับมา ─────────────
    def flush_buffer(self, current_time, link_map, packets_list, nodes_dict, log_func=None):
        if not self.buffer:
            return
        if current_time - self.last_flush_attempt < 2.0:
            return
        self.last_flush_attempt = current_time

        from packets import Packet   # import ที่นี่เพื่อหลีกเลี่ยง circular import

        to_remove = []
        for pkt in list(self.buffer):
            dst_id   = pkt.path[-1].id
            new_path = self.find_path_to(dst_id, link_map, nodes_dict)
            if new_path and len(new_path) > 1:
                new_pkt = Packet(pkt.msg, new_path, pkt.ptype)
                packets_list.append(new_pkt)
                to_remove.append(pkt)
                if log_func:
                    log_func(f"🔀 DTN flush @ {self.id} → {dst_id}", C_PACKET_DTN)

        for pkt in to_remove:
            try:
                self.buffer.remove(pkt)
            except ValueError:
                pass

    # ── update ทุก frame ──────────────────────────────────────────────
    def update(self):
        self.pulse += 0.08
