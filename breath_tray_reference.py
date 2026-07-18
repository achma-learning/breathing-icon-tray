# -*- coding: utf-8 -*-
"""
BreathTray - Guide de respiration dans la barre des taches Windows.
Affiche une icone animee + tooltip emoji qui suit un protocole de respiration
(inspiration / retention / expiration / retention).
"""

import threading
import time
import sys

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:
    print("Modules manquants. Lancez: python -m pip install pystray pillow")
    sys.exit(1)

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
}


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
                icon.icon = make_icon_image(label, progress, color)
                icon.title = "{0} {1} - {2}s  [{3}]".format(
                    emoji, label, remaining, state["protocol"])
                time.sleep(0.25)


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


def quit_app(icon, item):
    state["running"] = False
    icon.stop()


def main():
    menu = pystray.Menu(
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
    threading.Thread(target=breathing_loop, args=(icon,), daemon=True).start()
    icon.run()


if __name__ == "__main__":
    main()
