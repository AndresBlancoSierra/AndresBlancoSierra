#!/usr/bin/env python3
"""Genera el SVG unificado del perfil con estética terminal (paleta blanco/negro).

Salida: profile.svg — una sola ventana de terminal con:
  - Hero neofetch (logo Orion + info del sistema + stats GitHub)
  - Sección de proyectos
  - Streak y contacto
  - Constelaciones reales con deriva lenta animada
  - Cometas y lluvia matrix

Usa la API REST/GraphQL pública con token opcional para stats frescas.
"""
import os
import re
import json
import textwrap
import random
import urllib.request

USER_NAME = os.environ.get("USER_NAME", "AndresBlancoSierra")

# Paleta blanco/negro/escala de grises (estilo del portafolio personal)
BG = "#050505"
FG = "#f4f4f5"
DIM = "#a1a1aa"
DIM2 = "#71717a"
DIM3 = "#52525b"
BORDER = "#f4f4f5"
MONO = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
CW = 9.6  # ancho aprox de fuente 16px

# ---------------------------------------------------------------------------
# Datos reales de constelaciones (Hipparcos → proyección gnomónica)
# Extraídos de los SVGs previos del perfil.
# ---------------------------------------------------------------------------
CONSTELLATIONS = json.loads(r"""{
 "contact.svg": {"CAR": {"c": [["121.9","44.2","1.2"],["236.4","65.7","1.2"],["186.0","75.0","1.3"]], "l": [["186.0","75.0","236.4","65.7"]]}, "HER": {"c": [["59.2","64.9","1.0"],["269.8","58.2","1.4"],["64.4","32.9","1.0"],["326.8","59.3","1.3"]], "l": [["59.2","64.9","64.4","32.9"]]}, "CYG": {"c": [["296.8","69.8","1.4"],["205.7","26.2","1.3"],["183.0","63.6","1.0"],["45.5","79.0","1.0"],["135.0","43.5","1.1"]], "l": [["296.8","69.8","205.7","26.2"]]}},
 "dark_mode.svg": {"UMA": {"c": [["544.0","146.5","1.2"],["547.2","155.2","1.2"],["560.9","153.3","1.2"],["561.8","145.4","1.2"],["570.2","140.4","1.2"],["576.9","135.7","1.2"],["590.3","135.8","1.2"]], "l": [["544.0","146.5","547.2","155.2"],["547.2","155.2","560.9","153.3"],["560.9","153.3","561.8","145.4"],["561.8","145.4","544.0","146.5"],["561.8","145.4","570.2","140.4"],["570.2","140.4","576.9","135.7"],["576.9","135.7","590.3","135.8"]]}, "LEO": {"c": [["539.5","290.5","1.2"],["586.4","299.7","1.2"],["549.2","278.6","1.2"],["572.7","284.3","1.2"],["570.0","293.7","1.2"],["550.1","271.8","1.2"]], "l": [["550.1","271.8","549.2","278.6"],["549.2","278.6","570.0","293.7"],["570.0","293.7","539.5","290.5"],["539.5","290.5","572.7","284.3"],["572.7","284.3","586.4","299.7"],["549.2","278.6","572.7","284.3"]]}, "CYG": {"c": [["567.0","135.2","1.2"],["558.7","142.7","1.2"],["531.7","158.7","1.2"],["564.7","155.9","1.2"],["549.6","130.4","1.2"],["574.1","164.6","1.2"]], "l": [["564.7","155.9","549.6","130.4"],["558.7","142.7","564.7","155.9"],["558.7","142.7","574.1","164.6"],["567.0","135.2","238.7","142.7"],["558.7","142.7","531.7","158.7"]]}, "CRU": {"c": [["454.0","133.0","1.2"],["464.0","107.8","1.2"],["446.5","95.3","1.2"],["436.8","109.5","1.2"],["445.0","117.8","1.2"]], "l": [["446.5","95.3","454.0","133.0"],["464.0","107.8","436.8","109.5"],["446.5","95.3","436.8","109.5"],["464.0","107.8","454.0","133.0"],["454.0","133.0","445.0","117.8"]]}, "SGR": {"c": [["542.5","304.0","1.2"],["563.6","271.7","1.2"],["570.5","284.5","1.2"],["537.5","288.0","1.2"],["540.7","271.1","1.2"],["526.1","292.2","1.2"]], "l": [["526.1","292.2","542.5","304.0"],["542.5","304.0","537.5","288.0"],["537.5","288.0","563.6","271.7"],["563.6","271.7","570.5","284.5"],["570.5","284.5","540.7","271.1"],["540.7","271.1","537.5","288.0"],["540.7","271.1","526.1","292.2"]]}}
}""")

# Constelaciones por archivo origen para distribuir en el canvas unificado
POOL = []
for _file, consts in CONSTELLATIONS.items():
    for name, data in consts.items():
        POOL.append((name, data))

ARCH_ART = """\
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

LANG_ICONS = {
    "Python": "python",
    "TypeScript": "typescript",
    "JavaScript": "javascript",
    "C++": "cplusplus",
    "C": "c",
    "Java": "java",
    "Go": "go",
    "Rust": "rust",
    "HTML": "html5",
    "CSS": "css",
    "Shell": "gnubash",
    "Arduino": "arduino",
    "Vue": "vuedotjs",
    "Dart": "dart",
}


# ---------------------------------------------------------------------------
# Datos GitHub
# ---------------------------------------------------------------------------

def graphql(query):
    token = os.environ.get("GITHUB_TOKEN", "")
    headers = {"User-Agent": "profile-readme", "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers=headers,
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


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


def pinned_projects():
    q = """{ user(login: "USER") {
      pinnedItems(first: 6, types: REPOSITORY) {
        nodes { ... on Repository { name description primaryLanguage { name } } }
      } } }""".replace("USER", USER_NAME)
    try:
        data = graphql(q)
        nodes = data["data"]["user"]["pinnedItems"]["nodes"]
    except Exception as e:
        print(f"[warn] no se pudieron leer proyectos fijados: {e}")
        return []
    out = []
    for n in nodes:
        lang = (n.get("primaryLanguage") or {}).get("name", "")
        icon = LANG_ICONS.get(lang, "")
        out.append((n["name"], n["name"], n.get("description") or "", icon))
    return out


def visitor_count():
    try:
        req = urllib.request.Request(
            f"https://api.visitorbadge.io/api/visitors?path={USER_NAME}",
            headers={"User-Agent": "profile-readme"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            svg = r.read().decode()
        m = re.search(r"<title>VISITORS:?\s*(\d+)</title>", svg)
        if m:
            return m.group(1)
    except Exception as e:
        print(f"[warn] no se pudo obtener el contador de visitas: {e}")
    return ""


def streak_stats():
    total = 0
    cur_streak = 0
    longest = 0
    try:
        from datetime import datetime, timedelta
        today = datetime.now().date()
        start = datetime(2023, 3, 16).date()
        all_days = {}
        cursor = start
        while cursor < today:
            end = min(cursor + timedelta(days=364), today)
            q = ('{ user(login: "U") { contributionsCollection('
                 f'from: "{cursor}T00:00:00Z", to: "{end}T00:00:00Z") '
                 '{ contributionCalendar { totalContributions '
                 'weeks { contributionDays { contributionCount date } } } } } }').replace("U", USER_NAME)
            data = graphql(q)
            cal = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]
            total += cal["totalContributions"]
            for w in cal["weeks"]:
                for dd in w["contributionDays"]:
                    all_days[dd["date"]] = dd["contributionCount"]
            cursor = end + timedelta(days=1)

        run = 0
        for date_str, count in sorted(all_days.items()):
            run = run + 1 if count > 0 else 0
            longest = max(longest, run)
        today_str = today.isoformat()
        cur = 0
        day = today
        if all_days.get(today_str, 0) == 0:
            day = today - timedelta(days=1)
        while day.isoformat() in all_days and all_days[day.isoformat()] > 0:
            cur += 1
            day -= timedelta(days=1)
        cur_streak = cur
    except Exception as e:
        print(f"[warn] no se pudo calcular el streak: {e}")
    return {"total": total, "current": cur_streak, "longest": longest}


# ---------------------------------------------------------------------------
# Elementos del SVG unificado
# ---------------------------------------------------------------------------

def place_constellation(x, y, scale, data):
    """Devuelve círculos + líneas de una constelación, normalizada por su
    centroide y trasladada/escalada a (x, y)."""
    pts = [(float(cx), float(cy)) for cx, cy, _ in data["c"]]
    if not pts:
        return ""
    cxm = sum(p[0] for p in pts) / len(pts)
    cym = sum(p[1] for p in pts) / len(pts)
    parts = []
    for cx, cy, r in data["c"]:
        parts.append(f'<circle cx="{x + (float(cx) - cxm) * scale:.1f}" '
                     f'cy="{y + (float(cy) - cym) * scale:.1f}" '
                     f'r="1.2" fill="{FG}" opacity="0.65"/>')
    for x1, y1, x2, y2 in data["l"]:
        parts.append(f'<line x1="{x + (float(x1) - cxm) * scale:.1f}" '
                     f'y1="{y + (float(y1) - cym) * scale:.1f}" '
                     f'x2="{x + (float(x2) - cxm) * scale:.1f}" '
                     f'y2="{y + (float(y2) - cym) * scale:.1f}" '
                     f'stroke="{DIM}" stroke-width="0.5" opacity="0.35"/>')
    return "".join(parts)


def build_constellation_layer(svg_w, svg_h):
    """Coloca constelaciones reales en grupos independientes con deriva lenta."""
    random.seed(11)
    spots = [
        (0.10, 0.10, 1.0),   # esquina superior izquierda
        (0.84, 0.08, 0.9),
        (0.58, 0.14, 0.85),
        (0.42, 0.30, 0.9),
        (0.12, 0.38, 0.9),
        (0.86, 0.55, 1.0),
        (0.45, 0.70, 0.95),
        (0.10, 0.80, 0.85),
        (0.78, 0.86, 0.9),
        (0.50, 0.94, 0.9),
        (0.30, 0.55, 0.8),
        (0.68, 0.30, 0.75),
    ]
    groups = []
    css = []
    for i, (fx, fy, sc) in enumerate(spots):
        name, data = POOL[i % len(POOL)]
        x = fx * svg_w
        y = fy * svg_h
        dur = round(random.uniform(26, 38), 1)
        delay = round(random.uniform(-36, 0), 1)
        amp_x = round(random.uniform(10, 18), 1)
        amp_y = round(random.uniform(8, 13), 1)
        css.append(
            f'.c{i} {{ animation: drift{i} {dur}s ease-in-out infinite alternate; '
            f'animation-delay: {delay}s; }}'
        )
        css.append(
            f'@keyframes drift{i} {{ '
            f'0% {{ transform: translate(0,0); opacity: 0.5; }} '
            f'45% {{ opacity: 0.85; }} '
            f'100% {{ transform: translate({amp_x}px,{amp_y}px); opacity: 0.5; }} }}'
        )
        groups.append(
            f'<g class="c{i}"><g opacity="0.75">{place_constellation(x, y, sc, data)}</g></g>'
        )
    return "\n".join(groups), "\n".join(css)


def build_comets():
    """3 cometas globales con trayectoria diagonal, delays escalonados."""
    comet = []
    for i, (trail, head, dur, delay, w) in enumerate([
        (70, 2, 5, 0, 1.5),
        (60, 1.8, 6, 2, 1.2),
        (50, 1.5, 7, 4, 1.0),
    ]):
        comet.append(
            f'<g class="comet comet-{i + 1}">'
            f'<line x1="0" y1="0" x2="0" y2="{trail}" stroke="url(#comet-trail)" '
            f'stroke-width="{w}"/>'
            f'<circle cx="0" cy="0" r="{head}" fill="{FG}"/>'
            f'</g>'
        )
    css = (
        '.comet { opacity: 0; }\n'
        '.comet-1 { animation: comet1 5s ease-in-out infinite 0s; }\n'
        '@keyframes comet1 {\n'
        '  0% { transform: translate(860px, 40px); opacity: 0; }\n'
        '  5% { opacity: 0.9; }\n'
        '  40% { opacity: 0.9; }\n'
        '  50% { opacity: 0; }\n'
        '  100% { transform: translate(420px, 1800px); opacity: 0; }\n'
        '}\n'
        '.comet-2 { animation: comet2 6s ease-in-out infinite 2s; }\n'
        '@keyframes comet2 {\n'
        '  0% { transform: translate(790px, 80px); opacity: 0; }\n'
        '  5% { opacity: 0.8; }\n'
        '  35% { opacity: 0.8; }\n'
        '  45% { opacity: 0; }\n'
        '  100% { transform: translate(350px, 1720px); opacity: 0; }\n'
        '}\n'
        '.comet-3 { animation: comet3 7s ease-in-out infinite 4s; }\n'
        '@keyframes comet3 {\n'
        '  0% { transform: translate(920px, 20px); opacity: 0; }\n'
        '  4% { opacity: 0.7; }\n'
        '  30% { opacity: 0.7; }\n'
        '  40% { opacity: 0; }\n'
        '  100% { transform: translate(500px, 1880px); opacity: 0; }\n'
        '}\n'
    )
    return "<g id=\"comets\">" + "".join(comet) + "</g>", css


def build_rain(svg_w, svg_h):
    random.seed(7)
    rain_chars = "01アイウエオカキクケコサシスセソ$#%*+=-~^"
    cols = []
    for _ in range(18):
        x = random.randint(10, max(svg_w - 10, 20))
        dur = round(random.uniform(4.5, 9.0), 1)
        delay = round(random.uniform(-9.0, 0.0), 1)
        n = random.randint(6, 13)
        tsp = "".join(f'<tspan x="{x}" y="{24 + r * 24}">{c}</tspan>'
                      for r, c in enumerate(random.choice(rain_chars) for _ in range(n)))
        cols.append(f'<g class="rain" style="animation-duration:{dur}s;animation-delay:{delay}s">{tsp}</g>')
    return "<g id=\"rain\">" + "".join(cols) + "</g>"


def orion_logo():
    """Logo Orion (8 estrellas reales + 9 asterism lines), como en el hero previo."""
    stars = [
        (159.5, 136.6, 3.7, 0.93),
        (70.5, 272.7, 3.9, 1.00),
        (96.2, 145.1, 2.7, 0.56),
        (119.0, 209.8, 2.6, 0.54),
        (128.7, 216.2, 2.5, 0.48),
        (110.1, 196.8, 2.2, 0.39),
        (143.4, 285.0, 2.3, 0.43),
        (117.8, 115.0, 1.5, 0.30),
    ]
    lines = [
        (159.5, 136.6, 117.8, 115.0),
        (159.5, 136.6, 96.2, 145.1),
        (96.2, 145.1, 119.0, 209.8),
        (119.0, 209.8, 110.1, 196.8),
        (110.1, 196.8, 128.7, 216.2),
        (128.7, 216.2, 159.5, 136.6),
        (128.7, 216.2, 70.5, 272.7),
        (110.1, 196.8, 143.4, 285.0),
        (70.5, 272.7, 143.4, 285.0),
    ]
    s = "".join(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{FG}" opacity="{o}"/>'
                for cx, cy, r, o in stars)
    l = "".join(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{DIM}" stroke-width="1" opacity="0.6"/>'
                for x1, y1, x2, y2 in lines)
    return f'<g id="orion-logo">{s}{l}</g>'


def build_hero(stats, art, info_x, y0):
    logo_block = f'<g transform="translate(20, {y0 + 46})">{orion_logo()}</g>'

    info = [f'<text x="{info_x}" y="{y0 + 25}" fill="{FG}" font-size="16" font-family="{MONO}">']
    info.append(f'<tspan x="{info_x}" y="{y0 + 25}" class="glitch" fill="{FG}">andres@arch</tspan>'
                f'<tspan class="cursor" fill="{DIM2}">▌</tspan>'
                f'<tspan fill="{DIM}"> ─────────────────────────────</tspan>')
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
    yy = y0 + 55
    for k, v in rows:
        info.append(f'<tspan x="{info_x}" y="{yy}" fill="{DIM}">.</tspan>'
                    f'<tspan fill="{FG}">{k}</tspan>'
                    f'<tspan fill="{DIM}">: </tspan>'
                    f'<tspan fill="{FG}">{v}</tspan>')
        yy += 24
    yy += 6
    info.append(f'<tspan x="{info_x}" y="{yy}" fill="{FG}"> ─── GitHub Stats ───</tspan>')
    yy += 24
    info.append(f'<tspan x="{info_x}" y="{yy}" fill="{DIM}">.</tspan>'
                f'<tspan fill="{FG}">Repos</tspan><tspan fill="{DIM}">: {stats["repos"]:>4}</tspan>'
                f'<tspan fill="{DIM}">   </tspan><tspan fill="{FG}">Stars</tspan><tspan fill="{DIM}">: {stats["stars"]:>4}</tspan>')
    yy += 24
    info.append(f'<tspan x="{info_x}" y="{yy}" fill="{DIM}">.</tspan>'
                f'<tspan fill="{FG}">Followers</tspan><tspan fill="{DIM}">: {stats["followers"]:>4}</tspan>'
                f'<tspan fill="{DIM}">   </tspan><tspan fill="{FG}">Status</tspan><tspan fill="{DIM2}">: OPEN TO WORK</tspan>')
    info.append("</text>")
    return logo_block, "".join(info), yy + 40


def header_line(x, y, label):
    return (f'<text x="{x}" y="{y}" fill="{FG}" font-weight="bold">andres@arch</text>'
            f'<text x="{x + len("andres@arch") * CW}" y="{y}" fill="{DIM}" font-weight="bold">:~$ </text>'
            f'<text x="{x + len("andres@arch:~$ ") * CW}" y="{y}" fill="{DIM2}" font-weight="bold"># {label}</text>')


_ICON_CACHE = {}


def icon_path(name):
    if name in _ICON_CACHE:
        return _ICON_CACHE[name]
    path = ""
    try:
        req = urllib.request.Request(
            f"https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/{name}.svg",
            headers={"User-Agent": "profile-readme"},
        )
        with urllib.request.urlopen(req, timeout=15) as r:
            raw = r.read().decode()
        m = re.search(r'<path[^>]*d="([^"]+)"', raw)
        if m:
            path = f'<path d="{m.group(1)}" fill="{FG}"/>'
    except Exception as e:
        print(f"[warn] no se pudo descargar el icono {name}: {e}")
    _ICON_CACHE[name] = path
    return path


def build_projects(projects, x, y0):
    body = [header_line(x, y0 + 24, "ls ~/projects")]
    yy = y0 + 48
    for name, slug, desc, icon_name in projects:
        icon = icon_path(icon_name)
        icon_x = x + 20
        icon_size = 22
        icon_y = yy - icon_size + 6
        text_x = icon_x + (icon_size + 8 if icon else 0)
        lines = textwrap.wrap(desc or "", 96) or [desc or ""]
        chunk = []
        if icon:
            chunk.append(f'<g transform="translate({icon_x}, {icon_y})">'
                         f'<svg xmlns="http://www.w3.org/2000/svg" width="{icon_size}" height="{icon_size}" '
                         f'viewBox="0 0 24 24">{icon}</svg></g>')
        chunk.append(f'<text x="{text_x}" y="{yy}" fill="{DIM2}">▸ </text>'
                     f'<text x="{text_x + 2 * CW}" y="{yy}" fill="{FG}">{name}</text>')
        yy += 24
        for l in lines:
            chunk.append(f'<text x="{text_x}" y="{yy}" fill="{DIM}">{l}</text>')
            yy += 24
        chunk.append(f'<text x="{text_x}" y="{yy}" fill="{DIM3}">→ https://github.com/{USER_NAME}/{slug}</text>')
        yy += 24
        yy += 14
        body.append(f'<g>{ "".join(chunk) }</g>')
    return "".join(body), yy


def build_info_section(title, rows, x, y0):
    body = [header_line(x, y0 + 24, title)]
    yy = y0 + 48
    for k, v in rows:
        body.append(f'<text x="{x + 20}" y="{yy}" fill="{DIM2}">{k}</text>'
                    f'<text x="{x + 20 + (len(k) + 3) * CW}" y="{yy}" fill="{FG}">{v}</text>')
        yy += 24
    return "".join(body), yy + 10


def build():
    stats = public_stats()
    projects = pinned_projects()
    if not projects:
        print("[warn] no hay proyectos fijados, se usa la lista por defecto")
        projects = [
            ("what", "what", "Learn languages with songs: search, download and transcribe with Whisper.", "python"),
            ("cp2077-ui-react", "cp2077-ui-react", "Cyberpunk 2077 UI replica.", "react"),
            ("portrait-dataset-builder", "portrait-dataset-builder", "Dataset builder for portraits.", "python"),
            ("english-capture", "english-capture", "English listening/capture tool.", "python"),
            ("guitar-hero-controller", "guitar-hero-controller", "Custom controller for Guitar Hero.", "cplusplus"),
            ("opencode-telegram-controller", "opencode-telegram-controller", "Telegram controller for opencode.", "typescript"),
        ]
    whet = streak_stats()
    visitors = visitor_count()

    S = {}
    S["INFO_W"] = 701
    hero_art_w = 280

    hero_logo, hero_info, hero_h = build_hero(stats, ARCH_ART, 340, 46)

    # --- Proyectos ---
    proj_html, proj_end = build_projects(projects, 40, hero_h + 50)

    # --- Streak + contact lado a lado (ancho limitado) ---
    sec_w = 430
    streak_rows = [
        ("TOTAL", f"{whet['total']:,} contributions"),
        ("CURRENT", f"▸ {whet['current']} day{'s' if whet['current'] != 1 else ''}"),
        ("LONGEST", f"▸ {whet['longest']} day{'s' if whet['longest'] != 1 else ''}"),
    ]
    contact_rows = [
        ("EMAIL", "andresfelipeblancos15@gmail.com"),
        ("LOCATION", "Bogotá, Colombia · open to remote"),
        ("VISITORS", visitors or "?"),
        ("STATUS", "open to remote worldwide"),
    ]
    streak_html, streak_end = build_info_section("streak", streak_rows, 40, proj_end + 40)
    contact_html, contact_end = build_info_section("contact", contact_rows, 40 + sec_w, proj_end + 40)

    svg_h = max(contact_end, streak_end) + 34
    svg_w = 960

    # --- Constelaciones: capa de fondo (depende de la altura final) ---
    const_groups, const_css = build_constellation_layer(svg_w, svg_h)

    # --- Cometas ---
    comets_html, comet_css = build_comets()

    # --- Rain ---
    rain_html = build_rain(svg_w, svg_h)

    svg = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{svg_w}px" height="{svg_h}px" font-family="{MONO}" font-size="16px">
<defs>
<style>
text {{ white-space: pre; }}
.cursor {{ animation: blink 1.1s step-end infinite; }}
@keyframes blink {{ 50% {{ opacity: 0; }} }}
.rain {{ animation-name: fall; animation-timing-function: linear; animation-iteration-count: infinite; fill: {FG}; opacity: 0; }}
@keyframes fall {{
  0%   {{ transform: translateY(-120%); opacity: 0; }}
  10%  {{ opacity: 0.35; }}
  90%  {{ opacity: 0.25; }}
  100% {{ transform: translateY(120%); opacity: 0; }}
}}
.glitch {{ animation: glitch 3s steps(1) 1; }}
@keyframes glitch {{
  0%   {{ transform: translate(0); }}
  5%   {{ transform: translate(-2px, 1px); }}
  10%  {{ transform: translate(2px, -1px); }}
  15%  {{ transform: translate(-1px, 0); }}
  20%  {{ transform: translate(0); }}
  100% {{ transform: translate(0); }}
}}
.gfx {{ animation: glitchfx 11s steps(1) infinite; }}
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
.chan {{ animation: chsplit 11s steps(1) infinite; }}
@keyframes chsplit {{
  0%, 38% {{ opacity: 0; }}
  39%     {{ opacity: 0.9; }}
  45%     {{ opacity: 0; }}
  68%     {{ opacity: 0; }}
  69%     {{ opacity: 0.9; }}
  73%     {{ opacity: 0; }}
  100%    {{ opacity: 0; }}
}}
{const_css}
{comet_css}
</style>
<linearGradient id="comet-trail" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{FG}" stop-opacity="0"/>
  <stop offset="1" stop-color="{FG}" stop-opacity="0.8"/>
</linearGradient>
</defs>
<rect width="100%" height="100%" fill="{BG}" rx="12"/>

<!-- Barra de título de la ventana de terminal -->
<rect x="4" y="4" width="{svg_w - 8}" height="{svg_h - 8}" fill="none" stroke="{BORDER}" stroke-width="1" rx="10" opacity="0.35"/>
<circle cx="24" cy="24" r="5" fill="{DIM3}"/>
<circle cx="42" cy="24" r="5" fill="{DIM3}"/>
<circle cx="60" cy="24" r="5" fill="{DIM3}"/>
<text x="{svg_w // 2}" y="28" fill="{DIM}" font-size="13" text-anchor="middle" font-family="{MONO}">andres@arch — zsh</text>

<g id="constellations-bg">
{const_groups}
</g>

{rain_html}

{hero_logo}
{hero_info}

<g id="projects">
{proj_html}
</g>

<g id="streak">
{streak_html}
</g>

<g id="contact">
{contact_html}
</g>

{comets_html}
</svg>
'''
    return svg, svg_h


if __name__ == "__main__":
    svg, h = build()
    with open("profile.svg", "w") as f:
        f.write(svg)
    print(f"✓ profile.svg ({len(svg)} bytes, {h}px alto)")