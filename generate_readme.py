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
CONSTELLATIONS = json.loads(r"""{"contact.svg": {"CAR": {"c": [["121.9", "44.2", "1.2"], ["236.4", "65.7", "1.2"], ["186.0", "75.0", "1.3"]], "l": [["186.0", "75.0", "236.4", "65.7"]]}, "HER": {"c": [["59.2", "64.9", "1.0"], ["269.8", "58.2", "1.4"], ["64.4", "32.9", "1.0"], ["326.8", "59.3", "1.3"]], "l": [["59.2", "64.9", "64.4", "32.9"], ["326.8", "59.3", "269.8", "58.2"]]}, "CYG": {"c": [["333.1", "23.9", "1.4"], ["76.1", "34.5", "0.7"], ["71.9", "45.9", "0.8"], ["34.1", "15.9", "1.1"], ["48.7", "61.3", "0.7"]], "l": [["76.1", "34.5", "48.7", "61.3"]]}}, "dark_mode.svg": {"UMA": {"c": [["544.0", "146.5", "1.2"], ["547.2", "155.2", "1.2"], ["560.9", "153.3", "1.2"], ["561.8", "145.4", "1.2"], ["570.2", "140.4", "1.2"], ["576.9", "135.7", "1.2"], ["590.3", "135.8", "1.2"]], "l": [["544.0", "146.5", "547.2", "155.2"], ["547.2", "155.2", "560.9", "153.3"], ["560.9", "153.3", "561.8", "145.4"], ["561.8", "145.4", "544.0", "146.5"], ["561.8", "145.4", "570.2", "140.4"], ["570.2", "140.4", "576.9", "135.7"], ["576.9", "135.7", "590.3", "135.8"]]}, "LEO": {"c": [["539.5", "290.5", "1.2"], ["586.4", "299.7", "1.2"], ["549.2", "278.6", "1.2"], ["572.7", "284.3", "1.2"], ["570.0", "293.7", "1.2"], ["550.1", "271.8", "1.2"]], "l": [["550.1", "271.8", "549.2", "278.6"], ["549.2", "278.6", "570.0", "293.7"], ["570.0", "293.7", "539.5", "290.5"], ["539.5", "290.5", "572.7", "284.3"], ["572.7", "284.3", "586.4", "299.7"], ["549.2", "278.6", "572.7", "284.3"]]}, "CYG": {"c": [["567.0", "135.2", "1.2"], ["558.7", "142.7", "1.2"], ["531.7", "158.7", "1.2"], ["564.7", "155.9", "1.2"], ["549.6", "130.4", "1.2"], ["574.1", "164.6", "1.2"]], "l": [["564.7", "155.9", "549.6", "130.4"], ["558.7", "142.7", "564.7", "155.9"], ["558.7", "142.7", "574.1", "164.6"], ["567.0", "135.2", "238.7", "142.7"], ["558.7", "142.7", "531.7", "158.7"]]}, "CRU": {"c": [["454.0", "133.0", "1.2"], ["464.0", "107.8", "1.2"], ["446.5", "95.3", "1.2"], ["436.8", "109.5", "1.2"], ["445.0", "117.8", "1.2"]], "l": [["446.5", "95.3", "454.0", "133.0"], ["464.0", "107.8", "436.8", "109.5"], ["446.5", "95.3", "436.8", "109.5"], ["464.0", "107.8", "454.0", "133.0"], ["454.0", "133.0", "445.0", "117.8"]]}, "SGR": {"c": [["542.5", "304.0", "1.2"], ["563.6", "271.7", "1.2"], ["570.5", "284.5", "1.2"], ["537.5", "288.0", "1.2"], ["540.7", "271.1", "1.2"], ["526.1", "292.2", "1.2"]], "l": [["526.1", "292.2", "542.5", "304.0"], ["542.5", "304.0", "537.5", "288.0"], ["537.5", "288.0", "563.6", "271.7"], ["563.6", "271.7", "570.5", "284.5"], ["570.5", "284.5", "540.7", "271.1"], ["540.7", "271.1", "537.5", "288.0"], ["540.7", "271.1", "526.1", "292.2"]]}}, "light_mode.svg": {"UMA": {"c": [["544.0", "146.5", "1.2"], ["547.2", "155.2", "1.2"], ["560.9", "153.3", "1.2"], ["561.8", "145.4", "1.2"], ["570.2", "140.4", "1.2"], ["576.9", "135.7", "1.2"], ["590.3", "135.8", "1.2"]], "l": [["544.0", "146.5", "547.2", "155.2"], ["547.2", "155.2", "560.9", "153.3"], ["560.9", "153.3", "561.8", "145.4"], ["561.8", "145.4", "544.0", "146.5"], ["561.8", "145.4", "570.2", "140.4"], ["570.2", "140.4", "576.9", "135.7"], ["576.9", "135.7", "590.3", "135.8"]]}, "LEO": {"c": [["539.5", "290.5", "1.2"], ["586.4", "299.7", "1.2"], ["549.2", "278.6", "1.2"], ["572.7", "284.3", "1.2"], ["570.0", "293.7", "1.2"], ["550.1", "271.8", "1.2"]], "l": [["550.1", "271.8", "549.2", "278.6"], ["549.2", "278.6", "570.0", "293.7"], ["570.0", "293.7", "539.5", "290.5"], ["539.5", "290.5", "572.7", "284.3"], ["572.7", "284.3", "586.4", "299.7"], ["549.2", "278.6", "572.7", "284.3"]]}, "CYG": {"c": [["567.0", "135.2", "1.2"], ["558.7", "142.7", "1.2"], ["531.7", "158.7", "1.2"], ["564.7", "155.9", "1.2"], ["549.6", "130.4", "1.2"], ["574.1", "164.6", "1.2"]], "l": [["564.7", "155.9", "549.6", "130.4"], ["558.7", "142.7", "564.7", "155.9"], ["558.7", "142.7", "574.1", "164.6"], ["567.0", "135.2", "238.7", "142.7"], ["558.7", "142.7", "531.7", "158.7"]]}, "CRU": {"c": [["454.0", "133.0", "1.2"], ["464.0", "107.8", "1.2"], ["446.5", "95.3", "1.2"], ["436.8", "109.5", "1.2"], ["445.0", "117.8", "1.2"]], "l": [["446.5", "95.3", "454.0", "133.0"], ["464.0", "107.8", "436.8", "109.5"], ["446.5", "95.3", "436.8", "109.5"], ["464.0", "107.8", "454.0", "133.0"], ["454.0", "133.0", "445.0", "117.8"]]}, "SGR": {"c": [["542.5", "304.0", "1.2"], ["563.6", "271.7", "1.2"], ["570.5", "284.5", "1.2"], ["537.5", "288.0", "1.2"], ["540.7", "271.1", "1.2"], ["526.1", "292.2", "1.2"]], "l": [["526.1", "292.2", "542.5", "304.0"], ["542.5", "304.0", "537.5", "288.0"], ["537.5", "288.0", "563.6", "271.7"], ["563.6", "271.7", "570.5", "284.5"], ["570.5", "284.5", "540.7", "271.1"], ["540.7", "271.1", "537.5", "288.0"], ["540.7", "271.1", "526.1", "292.2"]]}}, "project-cp2077-ui-react.svg": {"SGR": {"c": [["626.0", "112.7", "1.1"], ["621.9", "27.4", "1.3"], ["315.1", "20.5", "1.4"], ["139.4", "113.0", "1.1"], ["758.6", "80.4", "1.1"], ["101.9", "21.1", "1.4"], ["213.3", "87.1", "1.3"], ["27.9", "88.5", "1.6"]], "l": []}, "VEL": {"c": [["638.2", "51.9", "0.9"], ["208.4", "58.5", "1.0"], ["79.1", "22.9", "1.2"], ["230.7", "97.1", "1.4"]], "l": [["230.7", "97.1", "208.4", "58.5"]]}, "CAR": {"c": [["570.1", "106.0", "1.1"], ["179.2", "98.7", "1.2"], ["241.0", "25.9", "1.7"], ["792.8", "106.9", "1.1"], ["317.5", "128.3", "1.2"], ["504.9", "105.7", "1.0"], ["670.4", "38.6", "1.1"], ["413.8", "72.2", "1.7"]], "l": [["179.2", "98.7", "241.0", "25.9"], ["413.8", "72.2", "504.9", "105.7"]]}, "PYX": {"c": [["487.3", "38.8", "1.0"], ["214.5", "128.6", "1.7"], ["115.6", "18.0", "0.9"], ["665.9", "119.1", "1.8"], ["326.3", "77.7", "1.7"]], "l": []}}, "project-english-capture.svg": {"PYX": {"c": [["78.9", "120.8", "1.0"], ["764.1", "29.9", "1.2"], ["387.0", "48.2", "1.5"], ["259.3", "106.2", "1.6"]], "l": []}, "CAS": {"c": [["620.9", "126.7", "1.3"], ["567.4", "62.0", "1.5"], ["702.4", "49.3", "1.2"], ["454.1", "19.0", "0.8"], ["698.4", "20.9", "1.1"], ["555.1", "45.2", "1.7"], ["168.3", "120.1", "1.0"], ["471.0", "16.5", "1.1"]], "l": [["555.1", "45.2", "454.1", "19.0"]]}, "VEL": {"c": [["298.7", "84.5", "1.2"], ["317.9", "37.8", "1.6"], ["740.8", "73.9", "1.3"], ["226.1", "26.4", "1.4"], ["91.4", "74.9", "1.3"], ["77.8", "33.3", "0.9"], ["714.8", "18.2", "0.8"], ["150.9", "34.0", "1.3"], ["762.9", "87.7", "1.1"], ["332.9", "107.5", "1.5"], ["251.8", "54.6", "1.4"]], "l": [["226.1", "26.4", "317.9", "37.8"], ["762.9", "87.7", "714.8", "18.2"]]}}, "project-guitar-hero-controller.svg": {"LEO": {"c": [["124.6", "43.7", "1.0"], ["645.1", "122.7", "1.8"], ["613.1", "67.1", "1.5"], ["717.1", "128.5", "1.2"], ["773.4", "113.8", "0.9"]], "l": [["613.1", "67.1", "645.1", "122.7"], ["717.1", "128.5", "773.4", "113.8"]]}, "VEL": {"c": [["756.3", "84.9", "1.8"], ["662.8", "36.0", "1.6"], ["110.2", "92.1", "1.1"], ["518.7", "73.6", "1.0"], ["265.7", "36.9", "1.8"], ["387.1", "59.2", "1.8"]], "l": [["756.3", "84.9", "662.8", "36.0"]]}, "SGR": {"c": [["173.0", "71.4", "1.0"], ["576.3", "37.6", "1.7"], ["189.8", "82.1", "1.2"], ["781.7", "37.9", "1.4"], ["566.5", "34.3", "1.1"], ["519.7", "125.3", "1.4"], ["311.1", "61.9", "0.9"]], "l": []}}, "project-opencode-telegram-controller.svg": {"COL": {"c": [["526.2", "71.3", "1.6"], ["422.2", "46.5", "1.5"], ["621.3", "64.5", "0.8"], ["172.2", "109.2", "1.7"], ["228.5", "114.1", "1.6"], ["23.6", "102.3", "0.9"], ["53.2", "117.9", "1.7"], ["396.4", "109.7", "1.1"]], "l": [["526.2", "71.3", "621.3", "64.5"]]}, "CYG": {"c": [["184.6", "57.0", "1.3"], ["404.9", "96.3", "1.4"], ["159.4", "49.6", "1.3"], ["293.7", "39.2", "1.3"], ["472.7", "78.9", "0.8"], ["473.0", "110.9", "1.3"], ["500.9", "106.0", "0.9"], ["524.2", "62.9", "0.9"]], "l": [["404.9", "96.3", "472.7", "78.9"], ["524.2", "62.9", "473.0", "110.9"]]}, "PEG": {"c": [["154.4", "80.6", "1.1"], ["532.7", "77.0", "1.4"], ["21.5", "111.6", "1.7"], ["593.5", "117.4", "1.6"], ["688.0", "24.9", "1.2"]], "l": [["532.7", "77.0", "593.5", "117.4"]]}, "VEL": {"c": [["789.7", "30.0", "1.1"], ["268.0", "48.0", "1.5"], ["598.8", "83.4", "1.1"], ["375.3", "28.4", "1.5"], ["46.8", "34.8", "1.3"]], "l": [["375.3", "28.4", "268.0", "48.0"]]}}, "project-portrait-dataset-builder.svg": {"HER": {"c": [["611.6", "44.4", "1.8"], ["181.4", "80.3", "1.1"], ["227.2", "34.5", "1.6"], ["587.2", "16.3", "1.4"], ["372.0", "117.1", "1.4"], ["223.1", "16.3", "1.6"]], "l": [["227.2", "34.5", "181.4", "80.3"]]}, "SGR": {"c": [["573.4", "84.9", "1.5"], ["118.1", "55.2", "1.6"], ["602.3", "70.9", "1.7"], ["191.7", "22.3", "0.9"], ["655.9", "104.2", "1.5"], ["180.3", "89.5", "1.4"], ["57.3", "47.9", "1.8"]], "l": [["191.7", "22.3", "118.1", "55.2"]]}, "SCO": {"c": [["229.4", "18.0", "1.3"], ["492.8", "46.8", "1.3"], ["565.2", "124.4", "1.6"], ["256.7", "103.7", "0.8"], ["503.7", "89.5", "1.6"], ["122.0", "103.8", "1.7"]], "l": []}}, "project-what.svg": {"PER": {"c": [["776.5", "112.0", "0.9"], ["136.8", "32.6", "1.5"], ["209.9", "127.7", "1.7"], ["500.5", "47.9", "1.3"], ["444.8", "52.4", "1.4"], ["389.9", "58.7", "1.4"], ["327.8", "81.5", "1.6"], ["744.3", "64.7", "1.7"]], "l": []}, "AUR": {"c": [["28.9", "91.0", "1.0"], ["108.5", "88.8", "1.4"], ["400.8", "108.2", "1.2"], ["266.0", "31.7", "1.2"], ["163.0", "74.1", "1.6"], ["680.5", "92.5", "1.4"], ["379.2", "83.6", "1.6"]], "l": []}, "PEG": {"c": [["634.9", "107.7", "1.6"], ["293.7", "68.9", "1.5"], ["723.5", "119.6", "1.3"], ["71.0", "124.2", "1.5"], ["74.9", "58.3", "1.0"], ["160.1", "94.6", "1.1"], ["78.9", "71.3", "1.5"]], "l": [["78.9", "71.3", "71.0", "124.2"]]}}, "streak.svg": {"HER": {"c": [["177.0", "26.0", "1.1"], ["159.0", "25.9", "1.1"], ["186.1", "21.4", "0.8"], ["166.7", "68.0", "1.3"]], "l": [["159.0", "25.9", "177.0", "26.0"], ["166.7", "68.0", "186.1", "21.4"]]}, "PEG": {"c": [["197.1", "71.1", "0.8"], ["105.8", "36.4", "0.9"], ["215.3", "41.4", "1.0"], ["143.2", "63.1", "1.0"], ["50.8", "59.9", "1.1"]], "l": []}}}""")

# Constelaciones por archivo origen para distribuir en el canvas unificado
POOL = []
for _file, consts in CONSTELLATIONS.items():
    for name, data in consts.items():
        if not any(existing == name for existing, _ in POOL):
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
    centroide y trasladada a (x, y). El `scale` es el diámetro objetivo (px):
    cada constelación se redimensiona según su extensión real, así las que
    vienen de SVGs de distinto tamaño se ven uniformes."""
    pts = [(float(cx), float(cy)) for cx, cy, _ in data["c"]]
    if not pts:
        return ""
    cxm = sum(p[0] for p in pts) / len(pts)
    cym = sum(p[1] for p in pts) / len(pts)
    ext = max(
        max(p[0] for p in pts) - min(p[0] for p in pts),
        max(p[1] for p in pts) - min(p[1] for p in pts),
    ) or 1.0
    k = scale / ext
    parts = []
    for cx, cy, r in data["c"]:
        parts.append(f'<circle cx="{x + (float(cx) - cxm) * k:.1f}" '
                     f'cy="{y + (float(cy) - cym) * k:.1f}" '
                     f'r="1.2" fill="{FG}" opacity="0.65"/>')
    for x1, y1, x2, y2 in data["l"]:
        parts.append(f'<line x1="{x + (float(x1) - cxm) * k:.1f}" '
                     f'y1="{y + (float(y1) - cym) * k:.1f}" '
                     f'x2="{x + (float(x2) - cxm) * k:.1f}" '
                     f'y2="{y + (float(y2) - cym) * k:.1f}" '
                     f'stroke="{DIM}" stroke-width="0.5" opacity="0.35"/>')
    return "".join(parts)


def build_constellation_layer(svg_w, svg_h):
    """Coloca constelaciones reales en grupos independientes con deriva lenta."""
    random.seed(11)
    spots = [
        (0.06, 0.08, 70),   # esquina superior izquierda
        (0.84, 0.06, 90),
        (0.58, 0.12, 85),
        (0.42, 0.28, 95),
        (0.12, 0.36, 100),
        (0.86, 0.52, 110),
        (0.45, 0.66, 105),
        (0.10, 0.78, 95),
        (0.78, 0.84, 110),
        (0.50, 0.92, 100),
        (0.30, 0.52, 90),
        (0.68, 0.30, 85),
        (0.22, 0.68, 85),
        (0.60, 0.46, 80),
        (0.92, 0.34, 90),
        (0.36, 0.44, 80),
        (0.16, 0.52, 90),
        (0.72, 0.62, 85),
    ]
    groups = []
    for i, (fx, fy, sc) in enumerate(spots):
        name, data = POOL[i % len(POOL)] if i < len(POOL) else (POOL[(i * 7) % len(POOL)])
        x = fx * svg_w
        y = fy * svg_h
        dur = round(random.uniform(10, 16), 1)
        tw = round(random.uniform(4, 7), 1)
        begin = round(random.uniform(-12, 0), 1)
        amp_x = round(random.uniform(18, 34), 1)
        amp_y = round(random.uniform(12, 24), 1)
        groups.append(
            '<g>'
            '<animateTransform attributeName="transform" type="translate" '
            f'values="0,0;{amp_x},{amp_y};0,0" dur="{dur}s" '
            'keySplines="0.42 0 0.58 1;0.42 0 0.58 1" calcMode="spline" '
            'repeatCount="indefinite"/>'
            '<animate attributeName="opacity" values="0.45;0.95;0.45" '
            f'dur="{tw}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<g opacity="0.75">{place_constellation(x, y, sc, data)}</g>'
            '</g>'
        )
    return "\n".join(groups), ""


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
    yy = y0 + 72
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
    yy = y0 + 72
    for k, v in rows:
        body.append(f'<text x="{x + 20}" y="{yy}" fill="{DIM2}">{k}</text>'
                    f'<text x="{x + 20 + (len(k) + 3) * CW}" y="{yy}" fill="{FG}">{v}</text>')
        yy += 24
    return "".join(body), yy + 10


def build_typewriter_name(text, x, y, size, caret_x_after=0, delay=300, speed=90):
    """Nombre grande con efecto máquina de escribir (SMIL, robusto en <img>).

    Replica el Typewriter del hero del sitio: cada carácter con begin escalonado
    (delay + i*speed) y caret que parpadea al final (keepCaret).
    """
    total = delay + len(text) * speed
    parts = [f'<text x="{x}" y="{y}" fill="{FG}" font-size="{size}" font-weight="600" font-family="{MONO}">']
    for i, ch in enumerate(text):
        begin = delay + i * speed
        parts.append(f'<tspan opacity="0"><animate attributeName="opacity" from="0" to="1" '
                     f'begin="{begin}ms" dur="1ms" fill="freeze"/>{ch}</tspan>')
    parts.append(f'<tspan fill="{DIM}" opacity="0"><animate attributeName="opacity" values="1;0;1" '
                 f'dur="1s" begin="{total + 200}ms" repeatCount="indefinite"/>▌</tspan>')
    parts.append('</text>')
    return "".join(parts)


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

    name_html = build_typewriter_name("Andres Blanco", 40, 150, 72)
    tagline_html = f'<text x="40" y="204" fill="{DIM}" font-size="24" font-weight="500" font-family="{MONO}">AIMING FURTHER</text>'

    hero_logo, hero_info, hero_h = build_hero(stats, ARCH_ART, 340, 210)

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
<text x="80" y="28" fill="{DIM}" font-size="13" font-family="{MONO}">andres@arch — zsh</text>

<g id="constellations-bg">
{const_groups}
</g>

{rain_html}

{name_html}
{tagline_html}

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