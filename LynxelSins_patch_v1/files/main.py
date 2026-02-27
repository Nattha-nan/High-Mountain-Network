"""
main.py — Entry Point
เหมือน "main scene" ใน Godot — รันไฟล์นี้เพื่อเริ่มโปรแกรม

ติดตั้ง:  pip install pygame-ce
รัน    :  python main.py

โครงสร้างไฟล์ (เหมือน Godot nodes):
  main.py        ← รันที่นี่  (Main Scene)
  simulator.py   ← game logic กลาง  (GameManager)
  nodes.py       ← Node class  (CharacterBody2D)
  links.py       ← Link class  (เส้นเชื่อม)
  packets.py     ← Packet class  (กระสุน/อนุภาค)
  ui.py          ← Button, ButtonBar, SidePanel  (Control nodes)
  config.py      ← ค่าคงที่ทั้งหมด  (Project Settings)
"""

import sys
try:
    import pygame
except ImportError:
    print("  ไม่พบ pygame  →  รัน:  pip install pygame-ce  แล้วลองใหม่")
    sys.exit(1)

from config    import W, H, FPS, NET_W, PANEL_BORDER, BG, BTN_BAR_H
from simulator import MountainNetSim
from ui        import ButtonBar, SidePanel


def main():
    pygame.init()
    pygame.font.init()

    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("🏔️🌐  High Mountain Network — Interactive Simulator")
    clock  = pygame.time.Clock()

    # ── fonts ─────────────────────────────────────────────────────────
    font_lg = pygame.font.SysFont("consolas", 20, bold=True)
    font_md = pygame.font.SysFont("consolas", 18)
    font_sm = pygame.font.SysFont("consolas", 16)
    font_xs = pygame.font.SysFont("consolas", 15)
    font_btn= pygame.font.SysFont("consolas", 16, bold=True)

    # ── objects ───────────────────────────────────────────────────────
    sim      = MountainNetSim()
    btn_bar  = ButtonBar(sim, font_btn)
    panel    = SidePanel()

    sim._log("🏔🌐  Welcome to High Mountain Network!", (88, 166, 255))
    sim._log("Click Node → Type messege → Select Send", (139, 148, 158))
    sim._log("Right Click = Cut/Connect Signal", (227, 179, 65))

    # ── game loop ─────────────────────────────────────────────────────
    while True:
        dt = clock.tick(FPS) / 1000.0

        # ── events ────────────────────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ปุ่ม Escape ออกจากโปรแกรม
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

            # พิมพ์ข้อความ
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    sim.do_send_from_input()
                elif ev.key == pygame.K_BACKSPACE:
                    sim.input_txt = sim.input_txt[:-1]
                elif ev.unicode and len(sim.input_txt) < 40:
                    sim.input_txt += ev.unicode

            # คลิกบนแผนที่
            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                if mx < NET_W and my < H - BTN_BAR_H:
                    for node in sim.nodes.values():
                        if node.hit(mx, my):
                            if ev.button == 1:   # คลิกซ้าย = เลือก
                                sim.selected = node.id
                                sim._log(f"🎯 เลือก: {node.id} ({node.type})",
                                         (255, 220, 80))
                            elif ev.button == 3: # คลิกขวา = toggle
                                sim.toggle_links_at(node)
                            break

            btn_bar.handle_event(ev)

        # ── update ────────────────────────────────────────────────────
        sim.update(dt)
        btn_bar.update(dt)

        # ── draw ──────────────────────────────────────────────────────
        screen.fill(BG)

        # แผนที่
        sim.draw_world(screen, font_sm, font_xs)

        # เส้นแบ่ง panel
        pygame.draw.line(screen, PANEL_BORDER, (NET_W, 0), (NET_W, H), 2)

        # แผง UI ขวา
        panel.draw(screen, (font_lg, font_md, font_sm, font_xs), sim)

        # แถวปุ่มด้านล่าง
        btn_bar.draw(screen)

        # topbar
        bar = pygame.Rect(0, 0, NET_W, 32)
        pygame.draw.rect(screen, (22, 27, 34), bar)
        pygame.draw.line(screen, PANEL_BORDER, (0, 32), (NET_W, 32))
        title = font_lg.render(
            "🌐  High Mountain Network — Interactive Simulator", True,
            (230, 237, 243)
        )
        screen.blit(title, (10, 7))

        pygame.display.flip()


if __name__ == "__main__":
    main()
