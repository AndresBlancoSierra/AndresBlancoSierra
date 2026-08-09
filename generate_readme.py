#!/usr/bin/env python3
"""Genera dark_mode.svg / light_mode.svg con stats de GitHub estilo neofetch.

Lado izquierdo: logo de Arch Linux en ASCII art con efectos CRT/glitch estilo
Vault-Tec (scanlines, flicker, noise, scanbar y glitch bursts periódicos con
desdoblamiento de canales RGB). Lado derecho: info del sistema + stats.
Usa solo la API REST pública (sin token): repos, stars y followers.
"""
import os
import urllib.request
import json
import random

USER_NAME = os.environ.get("USER_NAME", "AndresBlancoSierra")

ARCH_LOGO = """\
      _nnnn_
     dGGGGMMb
    @p~qp~~qMb
    M|@||@) M|
    @,----.JM|
   JS^\\__/  qKL
  dZP        qKRb
 dZP          qKKb
fZP            SMMb
HZM            MMMM
FqM            MMMM
__| ".        |\\dS"qML
|    `.       | `' \\Zq
_)      \\___,      .
\\____   )MMMMMP   .
     `-'       `--'
       ARCH LINUX""".splitlines()

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


def build_svg(theme):
    green = "#00ff41"
    dim_green = "#00cc33"
    fg = "#d9ffe2" if theme == "dark" else "#0a1f10"
    bg = "#050a07" if theme == "dark" else "#f0faf3"
    border = "#00ff41"
    accent = "#39ff14"
    magenta = "#ea36af"
    split_green = "#75fa69"

    s = stats
    art_lines = ARCH_LOGO
    art_width = max(len(l) for l in art_lines)
    art_height = len(art_lines)

    # columnas de texto a la derecha
    info_x = 15 + art_width * 9 + 45
    svg_w = info_x + 430

    tspans = []
    y = 25
    for line in art_lines:
        tspans.append(f'<tspan x="15" y="{y}">{line}</tspan>')
        y += 22

    # Matrix rain: columnas de caracteres que caen (CSS animation)
    rain_chars = "01アイウエオカキクケコサシスセソ$#%*+=-~^"
    random.seed(7)
    rain_cols = []
    n_cols = 14
    for _ in range(n_cols):
        x = random.randint(10, svg_w - 10)
        dur = round(random.uniform(4.5, 9.0), 1)
        delay = round(random.uniform(-9.0, 0.0), 1)
        col = "".join(random.choice(rain_chars) for _ in range(random.randint(6, 14)))
        tsp = "".join(
            f'<tspan x="{x}" y="{24 + r_idx * 22}">{c}</tspan>'
            for r_idx, c in enumerate(col)
        )
        rain_cols.append(
            f'<g class="rain" style="animation-duration:{dur}s;animation-delay:{delay}s">{tsp}</g>'
        )

    # panel de info
    info = []
    info.append(f'<text x="{info_x}" y="25" fill="{fg}" font-size="16" font-family="monospace">')
    info.append(f'<tspan x="{info_x}" y="25" class="glitch" fill="{green}">andres@arch</tspan>'
                f'<tspan class="cursor" fill="{accent}">▌</tspan>'
                f'<tspan fill="{dim_green}"> ─────────────────────────────</tspan>')
    rows = [
        ("OS", "Arch Linux + Hyprland"),
        ("WM", "Hyprland (Wayland)"),
        ("Shell", "bash/zsh"),
        ("Role", "Systems Engineer — EAN, Bogotá"),
        ("English", "B2"),
        ("Languages", "Python · TypeScript · C++ · Bash"),
        ("AI/ML", "Whisper · CLIP · OCR · InsightFace"),
        ("Backend", "FastAPI · SQLAlchemy"),
        ("Frontend", "React · Vite · Tailwind"),
        ("DevOps", "Docker · systemd · GitHub Actions"),
        ("Hardware", "Arduino · uinput · Wine"),
        ("Focus", "Applied AI + cyberpunk aesthetics"),
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
                f'<tspan fill="{dim_green}">   </tspan><tspan fill="{green}">Status</tspan><tspan fill="{accent}">: OPEN TO WORK</tspan>')
    info.append('</text>')

    svg_h = yy + 40

    # logo: base + 2 canales RGB offset (magenta/verde) que solo aparecen en el burst
    logo_base = "".join(tspans)
    chan_a = "".join(tspans).replace('x="15"', 'x="12"')
    chan_b = "".join(tspans).replace('x="15"', 'x="18"')
    logo_block = (
        f'<g class="logo-fx">'
        f'<text fill="{green}">{logo_base}</text>'
        f'<text class="chan" fill="{magenta}" transform="translate(-3,1)">{chan_a}</text>'
        f'<text class="chan" fill="{split_green}" transform="translate(3,-1)">{chan_b}</text>'
        f'</g>'
    )

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{svg_w}px" height="{svg_h}px" font-family="Consolas,Menlo,monospace" font-size="16px">
<defs>
<style>
text {{ white-space: pre; }}
.cursor {{
  animation: blink 1.1s step-end infinite;
}}
@keyframes blink {{
  50% {{ opacity: 0; }}
}}
.rain {{
  animation-name: fall;
  animation-timing-function: linear;
  animation-iteration-count: infinite;
  fill: {green};
  opacity: 0;
}}
@keyframes fall {{
  0%   {{ transform: translateY(-120%); opacity: 0; }}
  10%  {{ opacity: 0.35; }}
  90%  {{ opacity: 0.25; }}
  100% {{ transform: translateY(120%); opacity: 0; }}
}}
.glitch {{
  animation: glitch 3s steps(1) 1;
}}
@keyframes glitch {{
  0%   {{ transform: translate(0); }}
  5%   {{ transform: translate(-2px, 1px); }}
  10%  {{ transform: translate(2px, -1px); }}
  15%  {{ transform: translate(-1px, 0); }}
  20%  {{ transform: translate(0); }}
  100% {{ transform: translate(0); }}
}}
.logo-fx {{
  animation: glitchfx 11s steps(1) infinite;
}}
@keyframes glitchfx {{
  0%, 38% {{ transform: translate(0,0) skewX(0); }}
  39%     {{ transform: translate(-3px,1px) skewX(-2deg); }}
  41%     {{ transform: translate(4px,-2px) skewX(3deg); }}
  43%     {{ transform: translate(-2px,2px) skewX(-1deg); }}
  45%     {{ transform: translate(0,0) skewX(0); }}
  68%     {{ transform: translate(0,0) skewX(0); }}
  69%     {{ transform: translate(3px,-1px) skewX(2deg); }}
  71%     {{ transform: translate(-4px,1px) skewX(-3deg); }}
  73%     {{ transform: translate(0,0) skewX(0); }}
  100%    {{ transform: translate(0,0) skewX(0); }}
}}
.chan {{
  animation: chsplit 11s steps(1) infinite;
}}
@keyframes chsplit {{
  0%, 38% {{ opacity: 0; }}
  39%     {{ opacity: 0.9; }}
  45%     {{ opacity: 0; }}
  68%     {{ opacity: 0; }}
  69%     {{ opacity: 0.9; }}
  73%     {{ opacity: 0; }}
  100%    {{ opacity: 0; }}
}}
.flicker {{
  animation: screenflicker .15s infinite;
}}
@keyframes screenflicker {{
  0% {{ opacity: .04; }} 5% {{ opacity: .07; }} 10% {{ opacity: .04; }} 15% {{ opacity: .08; }}
  20% {{ opacity: .05; }} 25% {{ opacity: .07; }} 30% {{ opacity: .04; }} 35% {{ opacity: .06; }}
  40% {{ opacity: .08; }} 45% {{ opacity: .05; }} 50% {{ opacity: .06; }} 55% {{ opacity: .04; }}
  60% {{ opacity: .07; }} 65% {{ opacity: .05; }} 70% {{ opacity: .07; }} 75% {{ opacity: .04; }}
  80% {{ opacity: .06; }} 85% {{ opacity: .05; }} 90% {{ opacity: .07; }} 95% {{ opacity: .04; }}
  100% {{ opacity: .06; }}
}}
.noise {{
  animation: noisejump .35s steps(3) infinite;
}}
@keyframes noisejump {{
  0%   {{ transform: translate(0,0); }}
  33%  {{ transform: translate(-6px,3px); }}
  66%  {{ transform: translate(4px,-5px); }}
  100% {{ transform: translate(-2px,2px); }}
}}
.scanbar {{
  animation: scanbar 7s linear infinite;
}}
@keyframes scanbar {{
  0%   {{ transform: translateY(-90px); }}
  100% {{ transform: translateY({svg_h + 20}px); }}
}}
</style>
</defs>
<filter id="noise" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="2"/>
  <feColorMatrix type="saturate" values="0"/>
</filter>
<pattern id="scan" width="3" height="3" patternUnits="userSpaceOnUse">
  <rect width="3" height="1" fill="#000000"/>
</pattern>
<linearGradient id="sbg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{green}" stop-opacity="0"/>
  <stop offset="0.5" stop-color="{green}" stop-opacity="0.3"/>
  <stop offset="1" stop-color="{green}" stop-opacity="0"/>
</linearGradient>
<rect width="100%" height="100%" fill="{bg}" rx="12"/>
<rect x="4" y="4" width="{svg_w - 8}" height="{svg_h - 8}" fill="none" stroke="{border}" stroke-width="1" rx="10" opacity="0.35"/>
<g id="rain">{"".join(rain_cols)}</g>
{logo_block}
{"".join(info)}
<rect width="100%" height="100%" fill="url(#scan)" opacity="0.5"/>
<rect class="flicker" width="100%" height="100%" fill="#000000" opacity="0.04"/>
<rect class="noise" width="100%" height="100%" filter="url(#noise)" opacity="0.05"/>
<rect class="scanbar" width="100%" height="70" fill="url(#sbg)" opacity="0.35"/>
</svg>
'''
    return svg


if __name__ == "__main__":
    stats = public_stats()
    dark = build_svg("dark")
    light = build_svg("light")
    for name, content in (("dark_mode.svg", dark), ("light_mode.svg", light)):
        with open(name, "w") as f:
            f.write(content)
        print(f"✓ {name} ({len(content)} bytes)")
    print(f"stats: repos={stats['repos']} stars={stats['stars']} followers={stats['followers']}")
