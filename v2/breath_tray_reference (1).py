# -*- coding: utf-8 -*-
"""
BreathTray - Guide de respiration dans la barre des taches Windows.
- Icone animee (cercle qui grossit/retrecit) + tooltip emoji dans la zone de notification.
- Clic gauche sur l'icone : ouvre une grande fenetre centree (type "app") avec fond assombri
  et flou (effet Acrylic Windows 10/11), synchronisee sur la meme animation.
- Clic en dehors du popup, ou touche Echap : referme le popup.
"""

import threading
import time
import sys
import queue

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("Modules manquants. Lancez: python -m pip install pystray pillow")
    sys.exit(1)

try:
    import tkinter as tk
except ImportError:
    print("tkinter n'est pas disponible dans cette installation Python.")
    sys.exit(1)

import ctypes

# ---------------------------------------------------------------------------
# Protocoles predefinis : (nom, inspiration, retention_haute, expiration, retention_basse)
# ---------------------------------------------------------------------------
PROTOCOLS = {
    "Box Breathing (4-4-4-4)": (4, 4, 4, 4),
    "4-7-8 (relaxation)": (4, 7, 8, 0),
    "Coherence (5-0-5-0)": (5, 0, 5, 0),
    "Box lent (5-5-5-5)": (5, 5, 5, 5),
}

PHASES = ["Inspire", "Retiens", "Expire", "Retiens"]
EMOJIS = {"Inspire": "\U0001F7E2\u2B06", "Retiens": "\u270B",
          "Expire": "\U0001F535\u2B07", "Retiens_bas": "\u23F8"}
COLORS = {"Inspire": (46, 204, 113), "Retiens": (241, 196, 15),
          "Expire": (52, 152, 219), "Retiens_bas": (149, 165, 166)}

state = {
    "protocol": "Box Breathing (4-4-4-4)",
    "running": True,
    "paused": False,
    "phase": "Inspire",
    "progress": 0.0,
    "remaining": 4,
    "color": COLORS["Inspire"],
    "emoji": EMOJIS["Inspire"],
    "popup_visible": False,
}

command_queue = queue.Queue()


# ---------------------------------------------------------------------------
# Icone de la zone de notification
# ---------------------------------------------------------------------------
def make_icon_image(phase_label, progress, color):
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    min_r, max_r = 14, 28
    if phase_label == "Inspire":
        r = min_r + (max_r - min_r) * progress
    elif phase_label == "Expire":
        r = max_r - (max_r - min_r) * progress
    else:
        r = max_r
    cx = cy = size / 2
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (255,))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 220), width=3)
    return img


def phase_key(phase_label, index):
    return "Retiens" if index == 1 else ("Retiens_bas" if index == 3 else phase_label)


def breathing_loop(icon):
    while state["running"]:
        if state["paused"]:
            state["phase"] = "Pause"
            icon.title = "BreathTray - En pause (clic droit pour reprendre)"
            time.sleep(0.3)
            continue

        durations = PROTOCOLS[state["protocol"]]
        for idx, (label, seconds) in enumerate(zip(PHASES, durations)):
            if seconds <= 0:
                continue
            key = phase_key(label, idx)
            color = COLORS[key]
            emoji = EMOJIS[key]
            steps = max(int(seconds * 4), 1)
            for s in range(steps):
                if not state["running"]:
                    return
                while state["paused"]:
                    time.sleep(0.2)
                progress = s / steps
                remaining = round(seconds - (s / steps) * seconds)
                state["phase"] = label
                state["progress"] = progress
                state["remaining"] = remaining
                state["color"] = color
                state["emoji"] = emoji
                icon.icon = make_icon_image(label, progress, color)
                icon.title = "{0} {1} - {2}s  [{3}]".format(
                    emoji, label, remaining, state["protocol"])
                time.sleep(0.25)


# ---------------------------------------------------------------------------
# Effet "Acrylic" (flou Windows 10/11) via l'API non documentee
# SetWindowCompositionAttribute. Meilleur effort : si ca echoue (ancien
# Windows, restrictions), la fenetre reste juste en fond sombre uni.
# ---------------------------------------------------------------------------
def enable_acrylic(hwnd, tint):
    try:
        class ACCENT_POLICY(ctypes.Structure):
            _fields_ = [
                ("AccentState", ctypes.c_int),
                ("AccentFlags", ctypes.c_int),
                ("GradientColor", ctypes.c_uint),
                ("AnimationId", ctypes.c_int),
            ]

        class WCA_DATA(ctypes.Structure):
            _fields_ = [
                ("Attribute", ctypes.c_int),
                ("Data", ctypes.POINTER(ACCENT_POLICY)),
                ("SizeOfData", ctypes.c_size_t),
            ]

        accent = ACCENT_POLICY()
        accent.AccentState = 4  # ACCENT_ENABLE_ACRYLICBLURBEHIND
        accent.AccentFlags = 2
        accent.GradientColor = tint  # AABBGGRR
        data = WCA_DATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.SizeOfData = ctypes.sizeof(accent)
        data.Data = ctypes.pointer(accent)
        ctypes.windll.user32.SetWindowCompositionAttribute(hwnd, ctypes.pointer(data))
    except Exception:
        pass  # Pas bloquant : le popup reste utilisable sans le flou.


def get_toplevel_hwnd(widget):
    raw = widget.winfo_id()
    try:
        parent = ctypes.windll.user32.GetParent(raw)
        return parent if parent else raw
    except Exception:
        return raw


# ---------------------------------------------------------------------------
# Popup centre, plein ecran assombri/floute en fond
# ---------------------------------------------------------------------------
class BreathPopup:
    def __init__(self, root):
        self.root = root
        self._job = None
        self._acrylic_done = False

        # Fond plein ecran : assombrit + floute tout ce qu'il y a derriere.
        self.overlay = tk.Toplevel(root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.attributes("-alpha", 0.55)
        self.overlay.configure(bg="black")
        sw = self.overlay.winfo_screenwidth()
        sh = self.overlay.winfo_screenheight()
        self.overlay.geometry("{0}x{1}+0+0".format(sw, sh))
        self.overlay.bind("<Button-1>", lambda e: self.hide())
        self.overlay.bind("<Escape>", lambda e: self.hide())
        self.overlay.withdraw()

        # Fenetre principale : grande, centree.
        w, h = 460, 460
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.popup = tk.Toplevel(root)
        self.popup.overrideredirect(True)
        self.popup.attributes("-topmost", True)
        self.popup.geometry("{0}x{1}+{2}+{3}".format(w, h, x, y))
        self.popup.configure(bg="#141414")
        self.popup.bind("<Escape>", lambda e: self.hide())
        self.popup.bind("<FocusOut>", self._on_focus_out)
        self.popup.withdraw()

        self.w, self.h = w, h
        self.canvas = tk.Canvas(self.popup, width=w, height=h, bg="#141414",
                                 highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Escape>", lambda e: self.hide())

    def _on_focus_out(self, event):
        # Petit delai pour eviter de fermer sur un simple changement de focus interne.
        self.root.after(150, self._check_focus)

    def _check_focus(self):
        try:
            focused = self.root.focus_get()
        except Exception:
            focused = None
        if focused not in (self.popup, self.canvas):
            self.hide()

    def show(self):
        if state["popup_visible"]:
            return
        state["popup_visible"] = True
        self.overlay.deiconify()
        self.popup.deiconify()
        self.overlay.lower(self.popup)
        self.popup.lift()
        self.popup.focus_force()
        if not self._acrylic_done:
            self.root.after(60, self._apply_acrylic)
        self._tick()

    def _apply_acrylic(self):
        enable_acrylic(get_toplevel_hwnd(self.overlay), 0x40000000)
        enable_acrylic(get_toplevel_hwnd(self.popup), 0xCC1A1A1A)
        self._acrylic_done = True

    def hide(self):
        state["popup_visible"] = False
        if self._job:
            self.root.after_cancel(self._job)
            self._job = None
        self.popup.withdraw()
        self.overlay.withdraw()

    def toggle(self):
        if state["popup_visible"]:
            self.hide()
        else:
            self.show()

    def _tick(self):
        if not state["popup_visible"]:
            return
        self._draw()
        self._job = self.root.after(80, self._tick)

    def _draw(self):
        c = self.canvas
        c.delete("all")
        phase = state.get("phase", "Inspire")
        progress = state.get("progress", 0.0)
        remaining = state.get("remaining", 0)
        color = state.get("color", (46, 204, 113))
        emoji = state.get("emoji", "")
        hexcolor = "#%02x%02x%02x" % color
        min_r, max_r = 90, 170
        if phase == "Inspire":
            r = min_r + (max_r - min_r) * progress
        elif phase == "Expire":
            r = max_r - (max_r - min_r) * progress
        else:
            r = max_r
        cx, cy = self.w // 2, self.h // 2 - 25
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=hexcolor,
                      outline="#ffffff", width=3)
        c.create_text(cx, cy, text=emoji, font=("Segoe UI Emoji", 42), fill="white")
        c.create_text(cx, cy + r + 45, text=phase, font=("Segoe UI", 24, "bold"),
                      fill="white")
        c.create_text(cx, cy + r + 82, text="{0}s".format(remaining),
                      font=("Segoe UI", 16), fill="#cccccc")
        c.create_text(cx, self.h - 22, text=state.get("protocol", ""),
                      font=("Segoe UI", 10), fill="#888888")


# ---------------------------------------------------------------------------
# Menu de l'icone / actions
# ---------------------------------------------------------------------------
def build_protocol_menu():
    items = []
    for name in PROTOCOLS:
        def make_handler(n):
            def handler(icon, item):
                state["protocol"] = n
            return handler
        items.append(
            pystray.MenuItem(
                name, make_handler(name),
                checked=lambda item, n=name: state["protocol"] == n,
                radio=True,
            )
        )
    return items


def toggle_pause(icon, item):
    state["paused"] = not state["paused"]


def on_icon_activate(icon, item):
    command_queue.put("toggle")


def main():
    root = tk.Tk()
    root.withdraw()  # fenetre racine invisible, sert juste de parent Tk

    popup = BreathPopup(root)

    def poll_queue():
        try:
            while True:
                cmd = command_queue.get_nowait()
                if cmd == "toggle":
                    popup.toggle()
        except queue.Empty:
            pass
        root.after(100, poll_queue)

    def quit_app(icon, item):
        state["running"] = False
        icon.stop()
        root.after(0, root.quit)

    menu = pystray.Menu(
        pystray.MenuItem("Afficher / Masquer", on_icon_activate,
                          default=True, visible=False),
        pystray.MenuItem("Pause / Reprendre", toggle_pause),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Protocole", pystray.Menu(*build_protocol_menu())),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quitter", quit_app),
    )
    icon = pystray.Icon(
        "BreathTray",
        make_icon_image("Inspire", 0.0, COLORS["Inspire"]),
        "BreathTray",
        menu,
    )

    threading.Thread(target=icon.run, daemon=True).start()
    threading.Thread(target=breathing_loop, args=(icon,), daemon=True).start()

    poll_queue()
    root.mainloop()


if __name__ == "__main__":
    main()
