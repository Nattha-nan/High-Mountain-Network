"""
simulator.py — MountainNetSim (Game Manager / Main Scene)
เหมือน "Main.gd" ที่เชื่อม scene ต่างๆ ใน Godot
ทำหน้าที่: เก็บ state ทั้งหมด, update, draw
"""

import time
import random
from collections import deque

from config import (
    RAW_NODES, RAW_LINKS,
    NET_W, H, W, PANEL_BORDER, PANEL_BG, PANEL_W,
    C_GREEN, C_RED, C_YELLOW, C_MUTED, C_SEL,
    C_PACKET, C_PACKET_DTN, BTN_BAR_H
)
from nodes   import Node
from links   import Link
from packets import Packet


class MountainNetSim:
    """
    Game Manager — รู้จักทุก object ในเกม
    แต่ไม่วาดเองทั้งหมด — delegate ให้แต่ละ class draw ตัวเอง
    """

    def __init__(self):
        self.packets  = []
        self.log      = deque(maxlen=18)
        self.selected = None        # node id ที่เลือกเป็นปลายทาง
        self.input_txt = ""
        self.stats = {"sent": 0, "delivered": 0, "dropped": 0, "dtn_stored": 0}

        self._build_network()

    # ── สร้างเครือข่าย ────────────────────────────────────────────────
    def _build_network(self):
        self.nodes    = {nid: Node(nid, lbl, rx, ry, nt)
                         for nid, lbl, rx, ry, nt in RAW_NODES}
        self.links    = []
        self.link_map = {}
        for src_id, dst_id, bw, lt in RAW_LINKS:
            lnk = Link(self.nodes[src_id], self.nodes[dst_id], bw, lt)
            self.links.append(lnk)
            self.link_map[(src_id, dst_id)] = lnk

    # ── หา path ──────────────────────────────────────────────────────
    def _find_path(self, src_id, dst_id):
        """BFS บน alive links เท่านั้น"""
        from collections import deque as dq
        visited = {src_id}
        queue   = dq([[src_id]])
        adj     = {}
        for (a, b), lnk in self.link_map.items():
            if lnk.alive:
                adj.setdefault(a, []).append(b)
                adj.setdefault(b, []).append(a)
        while queue:
            path = queue.popleft()
            cur  = path[-1]
            if cur == dst_id:
                return [self.nodes[n] for n in path]
            for nxt in adj.get(cur, []):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(path + [nxt])
        return None

    def _find_path_any(self, src_id, dst_id):
        """BFS ไม่สนสถานะลิงก์ (สำหรับ DTN)"""
        from collections import deque as dq
        visited = {src_id}
        queue   = dq([[src_id]])
        all_adj = {}
        for (a, b) in self.link_map:
            all_adj.setdefault(a, []).append(b)
            all_adj.setdefault(b, []).append(a)
        while queue:
            path = queue.popleft()
            cur  = path[-1]
            if cur == dst_id:
                return [self.nodes[n] for n in path]
            for nxt in all_adj.get(cur, []):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(path + [nxt])
        return None

    # ── ส่งข้อความ ────────────────────────────────────────────────────
    def send_message(self, msg, dst_id, ptype="normal"):
        src_id = "GW"
        path   = self._find_path(src_id, dst_id)
        if path:
            pkt = Packet(msg, path, ptype)
            self.packets.append(pkt)
            self.stats["sent"] += 1
            self._log(f"📤 [{ptype.upper()}] '{msg[:20]}' → {dst_id}", C_PACKET)
        else:
            path_any = self._find_path_any(src_id, dst_id)
            if path_any:
                pkt = Packet(msg, path_any, "dtn")
                self.packets.append(pkt)
                self.stats["sent"] += 1
                self._log(f"🔀 [DTN] '{msg[:20]}' → {dst_id}", C_PACKET_DTN)
            else:
                self._log(f"❌ no path to {dst_id}", C_RED)

    # ── ปุ่ม callbacks ───────────────────────────────────────────────
    def do_send_from_input(self):
        """ปุ่ม Send — ส่งข้อความจาก input box"""
        if self.input_txt.strip() and self.selected:
            msg   = self.input_txt.strip()
            ptype = "emergency" if msg.startswith("!") else "normal"
            self.send_message(msg, self.selected, ptype)
            self.input_txt = ""
        elif not self.selected:
            self._log("⚠️  Click to select the destination node first.", C_YELLOW)
        else:
            self._log("⚠️  Type your message before pressing Send.", C_YELLOW)

    def do_random_chaos(self):
        """ปุ่ม Chaos — สุ่มตัดสัญญาณ"""
        for lnk in self.links:
            if not lnk.backup and random.random() < 0.25:
                lnk.alive = False
                lnk.flicker_timer = random.uniform(3.0, 8.0)
        self._log("⚡ chaos! Random link broken. (DTN would help)", C_RED)

    def do_reset_links(self):
        """ปุ่ม Reset — ฟื้นฟูทุกลิงก์"""
        for lnk in self.links:
            lnk.alive   = True
            lnk.quality = 1.0
        self._log("🔄 reset all link", C_GREEN)

    def do_clear_log(self):
        """ปุ่ม Clear Log"""
        self.log.clear()

    # ── log ──────────────────────────────────────────────────────────
    def _log(self, msg, color=None):
        self.log.append((msg, color or C_MUTED, time.time()))

    # ── toggle ลิงก์ของโหนด ──────────────────────────────────────────
    def toggle_links_at(self, node):
        for (a, b), lnk in self.link_map.items():
            if a == node.id or b == node.id:
                lnk.toggle()
                state = "✅ Normal" if lnk.alive else "❌ Lost"
                self._log(f"🔌 {a}↔{b}: {state}",
                          C_YELLOW if lnk.alive else C_RED)

    # ── update (เรียกทุก frame) ───────────────────────────────────────
    def update(self, dt):
        # อัปเดต links
        for lnk in self.links:
            lnk.update(dt)

        # DTN flush
        now = time.time()
        for node in self.nodes.values():
            node.flush_buffer(now, self.link_map, self.packets, self.nodes, self._log)

        # อัปเดต + เก็บ / ลบ packets
        for pkt in self.packets:
            pkt.update(self.link_map)
            if pkt.done:
                self.stats["delivered"] += 1
                self._log(f"✅-> Sent to {pkt.path[-1].id}: '{pkt.msg[:24]}'", C_GREEN)
                pkt.dead = True
            elif pkt.dead and not pkt.buffered:
                self.stats["dropped"] += 1
                self._log(f"❌X dropped: '{pkt.msg[:20]}'", C_RED)

        self.packets = [p for p in self.packets if not p.dead]

        # animation
        for node in self.nodes.values():
            node.update()

        # อัปเดต stats
        self.stats["dtn_stored"] = sum(len(n.buffer) for n in self.nodes.values())

    # ── draw (เรียกทุก frame) ─────────────────────────────────────────
    def draw_world(self, surf, font_sm, font_xs):
        """วาดแผนที่ (links + nodes + packets)"""
        for lnk in self.links:
            lnk.draw(surf)
        for node in self.nodes.values():
            node.draw(surf, font_xs, node.id == self.selected)
        for pkt in self.packets:
            pkt.draw(surf)
