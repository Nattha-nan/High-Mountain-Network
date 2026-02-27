"""
ui.py -- UI Widgets: Button, ButtonBar, SidePanel
Equivalent to Control nodes in Godot (Button, Label, Panel)
All buttons are defined here -- no keyboard shortcuts needed.
"""

import time
import pygame

from config import (
    W, H, NET_W, PANEL_W, PANEL_BG, PANEL_BORDER,
    C_TEXT, C_MUTED, C_GREEN, C_RED, C_YELLOW, C_SEL,
    C_INPUT_BG, C_INPUT_BD, C_PACKET, C_PACKET_EMG, C_PACKET_DTN,
    C_GATEWAY, C_BACKBONE, C_RELAY, C_VILLAGE, C_IOT,
    C_BTN_BG, C_BTN_HOVER, C_BTN_BORDER, C_BTN_TEXT,
    BTN_BAR_H
)


# ===============================================================
# Button
# ===============================================================
class Button:
    """A clickable button that triggers a callback on left-click."""

    def __init__(self, x, y, w, h, label, callback,
                 bg=None, hover=None, border=None, text_color=None, font=None):
        self.rect       = pygame.Rect(x, y, w, h)
        self.label      = label
        self.callback   = callback
        self.bg         = bg         or C_BTN_BG
        self.hover_col  = hover      or C_BTN_HOVER
        self.border_col = border     or C_BTN_BORDER
        self.text_col   = text_color or C_BTN_TEXT
        self._font      = font
        self.hovered    = False
        self.flash      = 0.0

    def handle_event(self, ev):
        if ev.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(ev.pos)
        elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
            if self.rect.collidepoint(ev.pos):
                self.callback()
                self.flash = 0.15
                return True
        return False

    def update(self, dt):
        if self.flash > 0:
            self.flash -= dt

    def draw(self, surf, font):
        f = self._font or font
        if self.flash > 0:
            bg = tuple(min(255, c + 40) for c in self.bg)
        elif self.hovered:
            bg = self.hover_col
        else:
            bg = self.bg
        pygame.draw.rect(surf, bg,              self.rect, border_radius=6)
        pygame.draw.rect(surf, self.border_col, self.rect, 1, border_radius=6)
        txt = f.render(self.label, True, self.text_col)
        surf.blit(txt, (
            self.rect.centerx - txt.get_width()  // 2,
            self.rect.centery - txt.get_height() // 2,
        ))


# ===============================================================
# ButtonBar -- horizontal row of buttons at the bottom of the map
# ===============================================================
class ButtonBar:
    """Replaces keyboard shortcuts with clickable buttons."""

    def __init__(self, sim, font):
        self.font    = font
        self.buttons = []
        self._build(sim)

    def _build(self, sim):
        y   = H - BTN_BAR_H + 6
        bh  = BTN_BAR_H - 12
        gap = 6

        defs = [
            ("-> Send",          sim.do_send_from_input,                                       (40, 70, 40), C_GREEN),
            ("! Chaos",          sim.do_random_chaos,                                           (70, 30, 30), C_RED),
            ("<- Reset Links",   sim.do_reset_links,                                            (30, 50, 70), (88, 166, 255)),
            ("_ Clear Log",      sim.do_clear_log,                                              C_BTN_BG,     C_BTN_BORDER),
            (":D Greet->VA",     lambda: sim.send_message("Hello there!", "VA", "normal"),      (50, 60, 30), C_VILLAGE),
            ("!! Emergency->VD", lambda: sim.send_message("!fire emergency!", "VD","emergency"),(80, 30, 30), C_PACKET_EMG),
            ("? Sensor->S1",     lambda: sim.send_message("sensor_batch", "S1", "normal"),      (30, 55, 60), C_IOT),
        ]

        bw = (NET_W - gap * (len(defs) + 1)) // len(defs)
        x  = gap
        for label, cb, bg, border in defs:
            self.buttons.append(
                Button(x, y, bw, bh, label, cb, bg=bg, border=border, font=self.font)
            )
            x += bw + gap

    def handle_event(self, ev):
        for btn in self.buttons:
            btn.handle_event(ev)

    def update(self, dt):
        for btn in self.buttons:
            btn.update(dt)

    def draw(self, surf):
        pygame.draw.rect(surf, (18, 22, 28),
                         pygame.Rect(0, H - BTN_BAR_H, NET_W, BTN_BAR_H))
        pygame.draw.line(surf, PANEL_BORDER,
                         (0, H - BTN_BAR_H), (NET_W, H - BTN_BAR_H))
        for btn in self.buttons:
            btn.draw(surf, self.font)


# ===============================================================
# SidePanel -- right-side control panel
# ===============================================================
class SidePanel:
    """Displays stats, destination, input box, legend, and event log."""

    CHAR_W = 7  # approx pixel width per char for font_xs (consolas size 10)

    def draw(self, surf, fonts, sim):
        font_lg, font_md, font_sm, font_xs = fonts
        px = NET_W + 8
        pygame.draw.rect(surf, PANEL_BG, (NET_W, 0, PANEL_W, H))

        y = 10

        # title
        surf.blit(font_lg.render("  Control Panel", True, (88, 166, 255)), (px, y))
        y += 22
        self._divider(surf, y); y += 8

        # statistics
        surf.blit(font_md.render("Statistics", True, C_MUTED), (px, y)); y += 16
        st = sim.stats
        for txt, col in [
            (f"Sent     : {st['sent']}",      C_TEXT),
            (f"Delivered: {st['delivered']}",  C_GREEN),
            (f"Dropped  : {st['dropped']}",    C_RED),
            (f"DTN buf  : {st['dtn_stored']}", C_PACKET_DTN),
        ]:
            surf.blit(font_sm.render(txt, True, col), (px, y)); y += 14
        y += 4
        self._divider(surf, y); y += 8

        # destination
        surf.blit(font_md.render("Destination  (Click Node On The Map)", True, C_MUTED), (px, y))
        y += 16
        sel_lbl = sim.selected or "(Not Selected)"
        col     = C_SEL if sim.selected else C_MUTED
        surf.blit(font_sm.render(f"> {sel_lbl}", True, col), (px, y)); y += 18
        self._divider(surf, y); y += 8

        # message input box
        surf.blit(font_md.render("Message  (! = emergency)", True, C_MUTED), (px, y)); y += 16
        box = pygame.Rect(NET_W + 4, y, PANEL_W - 12, 26)
        pygame.draw.rect(surf, C_INPUT_BG, box, border_radius=4)
        pygame.draw.rect(surf, C_INPUT_BD, box, 1, border_radius=4)
        cursor = "|" if int(time.time() * 2) % 2 == 0 else " "
        surf.blit(font_md.render(sim.input_txt + cursor, True, C_TEXT), (box.x + 5, box.y + 5))
        y += 32
        self._divider(surf, y); y += 8

        # hints
        for hint, col in [
            ("Click node = Select destination",  C_MUTED),
            ("Right-click node = Toggle signal", C_YELLOW),
            ("Use buttons below to control",     (88, 166, 255)),
        ]:
            surf.blit(font_xs.render(hint, True, col), (px, y)); y += 13
        y += 4
        self._divider(surf, y); y += 8

        # legend
        surf.blit(font_md.render("Legend", True, C_MUTED), (px, y)); y += 15
        legend = [
            ("● Gateway",    C_GATEWAY),   ("● Backbone",  C_BACKBONE),
            ("● Relay",      C_RELAY),     ("● Village",   C_VILLAGE),
            ("● IoT",        C_IOT),       ("- Fiber",     C_GATEWAY),
            ("- Microwave",  C_BACKBONE),  ("- Wi-Fi",     C_VILLAGE),
            ("-- Backup",    C_RELAY),     ("● Packet",    C_PACKET),
            ("● Emergency",  C_PACKET_EMG),("● DTN",       C_PACKET_DTN),
        ]
        for i, (lbl, col) in enumerate(legend):
            surf.blit(font_xs.render(lbl, True, col),
                      (px + (160 if i % 2 else 0), y))
            if i % 2:
                y += 13
        if len(legend) % 2:
            y += 13
        y += 4
        self._divider(surf, y); y += 8

        # event log with word-wrap
        surf.blit(font_md.render("Event Log", True, C_MUTED), (px, y)); y += 15
        max_chars  = (PANEL_W - 16) // self.CHAR_W
        log_bottom = H - BTN_BAR_H - 5

        for msg, col, ts in list(sim.log):
            if y >= log_bottom:
                break
            elapsed = time.time() - ts
            alpha_f = max(0.3, 1.0 - elapsed / 30.0)
            r, g, b = col
            fade    = (int(r * alpha_f), int(g * alpha_f), int(b * alpha_f))

            # split into lines that fit the panel width
            words = msg.split(" ")
            line  = ""
            for word in words:
                candidate = (line + " " + word).strip()
                if len(candidate) > max_chars and line:
                    surf.blit(font_xs.render(line, True, fade), (px, y))
                    y += 13
                    line = word
                    if y >= log_bottom:
                        break
                else:
                    line = candidate
            if line and y < log_bottom:
                surf.blit(font_xs.render(line, True, fade), (px, y))
                y += 13

    def _divider(self, surf, y):
        pygame.draw.line(surf, PANEL_BORDER, (NET_W + 4, y), (W - 4, y))