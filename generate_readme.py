#!/usr/bin/env python3
"""Genera dark_mode.svg / light_mode.svg con stats de GitHub en estilo neofetch Matrix.

Usa solo la API REST pública (sin token): repos, stars y followers.
La foto del perfil se convierte a ASCII art en el mismo paso (foto.jpg).
"""
import os
import urllib.request
import json
import base64

USER_NAME = os.environ.get("USER_NAME", "AndresBlancoSierra")
PHOTO = "foto.jpg"

ASCII_ART = [
    "======---------===-----------:::::------------::.:::::::",
    "========-----+###*------:::::::::::--------:::..::----::",
    "===========--=%@%+-----::::::...::::::::::::...:::------",
    "===========-==*%*------:::::...:::::::::::.....:::::::::",
    ".......:::--+*==+=:--::-==+++=--:::::::::...::::::::::::",
    "----:::::.:=++:=+-...-+*####%##**-..:::....:::::::::::::",
    "==========-:-===-::-+*%%@@@@@@%###-..       .....::::::-",
    "=---------:::=+++--=%%%@@%%@@@%#@%*..                 ..",
    "=---------:=#%%%*==-*%#%%#*##*+-*%*.  .............:::::",
    "==--------+*+=**=:::=+=++==++=-::+=             ...::--=",
    "=--=-----=*==+##-::::==-=++++=:..==:.:-.       ...::-===",
    "**+++++-=*+=+#%#==---=++***++=:.=*: . .--:   ...:-======",
    "******-=*+++*#%#*#*++++****+==-=*+=--...:=-:..-=++===--:",
    "+++++-=**++*#%%#*#++++-=#%%#**#%@#+=*==--=-----=+=-:..:-",
    "+++=-+*#++*#%%@#**+=-.:=#@%###%%%%*+*=..+*=====--:..--::",
    "+=--+**+=+%#%%%*+=...:-*#+==+*#%%@%*+-..**++++++++==:   ",
    "=--=+**==#%#%%%=..:=+=+#*+**#%%@@#**++-:=====+++**++=-. ",
    "--=+***-*%%%#%#==++=++==*+**#%@%###***#=+==--+=:-=****#-",
    "=+*****+#%#@##*++*+==+-.-:--*#%*#%%#**%#++==+++==:=##%%-",
    "+******#%@#@###*+#++=+---:-=*##+*%%%###%#++++++*******+=",
    "+****##%%%%%%#%#**#+===+=-=+*#*+#@@@%%%@@#*+++******++*+",
    "++**##%@#@%%*%#++**=++**=+******####%%%@%*+++++++=++***",
    "*****%%%@#@#%+##*--=+####*####**+**#######+===++==+**##*",
    "****#@%%#%@#%+###*=-=#@@@@@@@#**++++*****++======+=+####",
    "***#%@%@#@%%#+#####*-+@@%%%%%#*+=====++++++====++=..:+##",
    "*###@@%@#@#%**%%#####+*%##*##**+=----============-:..:=+",
    "###%@%@%%#@*%%##########***+++**+++=============+:. .:.",
    "###%@%@#@@#@*%###############%*=++++++++++=====-++::....",
]

# Stats vía REST pública (sin token, funciona en Actions con el rate limit compartido)
def public_stats():
    stats = {"repos": 0, "stars": 0, "followers": 0}
    try:
        req = urllib.request.Request(
            f"https://api.github.com/users/{USER_NAME}",
            headers={"User-Agent": "profile-readme", "Accept": "application/vnd.github+json"},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            user = json.loads(r.read())
        stats["repos"] = int(user.get("public_repos", 0))
        stats["followers"] = int(user.get("followers", 0))

        page = 1
        while True:
            req = urllib.request.Request(
                f"https://api.github.com/users/{USER_NAME}/repos?per_page=100&page={page}&type=owner",
                headers={"User-Agent": "profile-readme", "Accept": "application/vnd.github+json"},
            )
            with urllib.request.urlopen(req, timeout=30) as r:
                repos = json.loads(r.read())
            if not repos:
                break
            stats["stars"] += sum(int(rp.get("stargazers_count", 0)) for rp in repos)
            if len(repos) < 100:
                break
            page += 1
    except Exception as e:
        print(f"[warn] no se pudieron obtener stats públicas: {e}")
    return stats


def photo_ascii(width=56):
    """Re-genera el ASCII art desde foto.jpg (fallback al ASCII embebido)."""
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return ASCII_ART

    try:
        img = Image.open(PHOTO).convert("L")
        img = ImageOps.autocontrast(img, cutoff=2)
        img = ImageOps.invert(img)
        aspect = img.height / img.width
        height = max(1, int(round(width * aspect * 0.5)))
        img = img.resize((width, height))
        chars = " .:-=+*#%@"
        lines = []
        for y in range(height):
            row = "".join(
                chars[min(9, px * len(chars) // 256)] for px in [img.getpixel((x, y)) for x in range(width)]
            )
            lines.append(row)
        return lines
    except Exception:
        return ASCII_ART


def build_svg(theme, art):
    green = "#00ff41"
    dim_green = "#00cc33"
    fg = "#d9ffe2" if theme == "dark" else "#0a1f10"
    bg = "#050a07" if theme == "dark" else "#f0faf3"
    panel = "#0a140d" if theme == "dark" else "#e6f5ea"
    border = "#00ff41"
    accent = "#39ff14"

    s = stats
    art_lines = art
    art_width = max(len(l) for l in art_lines)
    art_height = len(art_lines)

    # columnas de texto a la derecha
    info_x = 15 + art_width * 9 + 25
    svg_w = info_x + 430

    tspans = []
    y = 25
    for line in art_lines:
        tspans.append(f'<tspan x="15" y="{y}">{line}</tspan>')
        y += 22

    # panel de info
    info = []
    info.append(f'<text x="{info_x}" y="25" fill="{fg}" font-size="16" font-family="monospace">')
    info.append(f'<tspan x="{info_x}" y="25" fill="{green}">andres@arch</tspan><tspan fill="{dim_green}"> ─────────────────────────────</tspan>')
    rows = [
        ("OS", "Arch Linux + Hyprland"),
        ("WM", "Hyprland (Wayland)"),
        ("Shell", "bash/zsh"),
        ("Rol", "Ing. Sistemas — EAN, Bogotá"),
        ("Inglés", "B2"),
        ("Lenguajes", "Python · TypeScript · C++ · Bash"),
        ("IA/ML", "Whisper · CLIP · OCR · InsightFace"),
        ("Backend", "FastAPI · SQLAlchemy"),
        ("Frontend", "React · Vite · Tailwind"),
        ("DevOps", "Docker · systemd · GitHub Actions"),
        ("Hardware", "Arduino · uinput · Wine"),
        ("Focus", "IA aplicada + estética cyberpunk"),
    ]
    yy = 55
    for k, v in rows:
        info.append(f'<tspan x="{info_x}" y="{yy}" fill="{dim_green}">.</tspan>'
                    f'<tspan fill="{green}">{k}</tspan>'
                    f'<tspan fill="{dim_green}">: </tspan>'
                    f'<tspan fill="{fg}">{v}</tspan>')
        yy += 24

    yy += 6
    info.append(f'<tspan x="{info_x}" y="{yy}" fill="{green}"> ─── GitHub Stats ───</tspan>')
    yy += 24
    info.append(f'<tspan x="{info_x}" y="{yy}" fill="{dim_green}">.</tspan>'
                f'<tspan fill="{green}">Repos</tspan><tspan fill="{dim_green}">: {s["repos"]:>4}</tspan>'
                f'<tspan fill="{dim_green}">   </tspan><tspan fill="{green}">Stars</tspan><tspan fill="{dim_green}">: {s["stars"]:>4}</tspan>')
    yy += 24
    info.append(f'<tspan x="{info_x}" y="{yy}" fill="{dim_green}">.</tspan>'
                f'<tspan fill="{green}">Followers</tspan><tspan fill="{dim_green}">: {s["followers"]:>4}</tspan>'
                f'<tspan fill="{dim_green}">   </tspan><tspan fill="{green}">Estado</tspan><tspan fill="{accent}">: OPEN TO WORK</tspan>')
    info.append('</text>')

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}px" height="{y + 40}px" font-family="Consolas,Menlo,monospace" font-size="16px">
<defs>
<style>
text {{ white-space: pre; }}
</style>
</defs>
<rect width="100%" height="100%" fill="{bg}" rx="12"/>
<rect x="4" y="4" width="{svg_w - 8}" height="{y + 32}" fill="none" stroke="{border}" stroke-width="1" rx="10" opacity="0.35"/>
<text fill="{green}">
{"".join(tspans)}
</text>
{"".join(info)}
</svg>
'''
    return svg


if __name__ == "__main__":
    stats = public_stats()
    art = photo_ascii()
    dark = build_svg("dark", art)
    light = build_svg("light", art)
    for name, content in (("dark_mode.svg", dark), ("light_mode.svg", light)):
        with open(name, "w") as f:
            f.write(content)
        print(f"✓ {name} ({len(content)} bytes)")
    print(f"stats: repos={stats['repos']} stars={stats['stars']} followers={stats['followers']}")
