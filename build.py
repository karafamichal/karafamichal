"""Builds assets/*.svg with subset Google Fonts inlined (GitHub can't load web fonts inside <img> SVGs).
Run: python build.py
"""
import base64, re, urllib.request, urllib.parse
from pathlib import Path

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"
NAVY, LINE, WIRE, BLUE, AMBER, FOG, WHITE = "#182231", "#24324A", "#3A4D6B", "#5AA1F7", "#F5B941", "#C3CEDD", "#FFFFFF"
OUT = Path(__file__).parent / "assets"


def fonts_css(text):
    """Fetch only the glyphs in `text` and return @font-face rules with data: URIs."""
    q = urllib.parse.urlencode({"family": ["Archivo:wdth,wght@100,400;100,600;125,800", "IBM Plex Mono:wght@400;500", "Doto:wght@800"],
                                "text": text, "display": "block"}, doseq=True)
    css = urllib.request.urlopen(urllib.request.Request("https://fonts.googleapis.com/css2?" + q, headers={"User-Agent": UA})).read().decode()
    def inline(m):
        data = urllib.request.urlopen(urllib.request.Request(m.group(1), headers={"User-Agent": UA})).read()
        return "url(data:font/woff2;base64,%s)" % base64.b64encode(data).decode()
    css = re.sub(r"url\((https://[^)]+)\)", inline, css)
    return re.sub(r"\s*unicode-range:[^;]+;", "", css)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def svg(w, h, body, title):
    text = re.sub(r"<[^>]+>", "", body) + title
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
{fonts_css(''.join(sorted(set(text))) )}
.d{{font-family:Archivo;font-stretch:125%;font-weight:800}}
.b{{font-family:Archivo;font-weight:400}}
.s{{font-family:Archivo;font-weight:600}}
.m{{font-family:'IBM Plex Mono';font-weight:400}}
.x{{font-family:Doto;font-weight:800}}
.pkt{{animation:go var(--t) linear infinite;animation-delay:var(--d);offset-rotate:0deg}}
@keyframes go{{from{{offset-distance:0%}}to{{offset-distance:100%}}}}
.led{{animation:blink 2.4s steps(1) infinite}}
@keyframes blink{{50%{{opacity:.25}}}}
@media (prefers-reduced-motion:reduce){{.pkt,.led{{animation:none}}.pkt{{offset-distance:50%}}}}
</style>
<rect width="{w}" height="{h}" rx="18" fill="{NAVY}"/>
{body}
</svg>"""


def hero():
    W, H = 1280, 480
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1.4" fill="{LINE}"/>' for x in range(40, W, 32) for y in range(40, H, 32))
    # three MikroTik sites, meshed with VPN tunnels, OSPF on top; two machines per site
    A, B, C = (790, 240), (980, 240), (1170, 240)
    servers = [(r[0] + dx, 340) for r in (A, B, C) for dx in (-42, 42)]
    drop = lambda r: (r[0], r[1] + 52)  # cables start below the router label
    os_names = ["proxmox", "debian", "proxmox", "ubuntu", "debian", "proxmox"]
    line = lambda p, q, extra="": f'<line x1="{p[0]}" y1="{p[1]}" x2="{q[0]}" y2="{q[1]}" stroke="{WIRE}" stroke-width="2" {extra}/>'
    arc = f"M{A[0]} {A[1]} Q{B[0]} 60 {C[0]} {C[1]}"
    dash = 'stroke-dasharray="7 7"'
    links = line(A, B, dash) + line(B, C, dash) + f'<path d="{arc}" fill="none" stroke="{WIRE}" stroke-width="2" {dash}/>'
    links += "".join(line(drop((A, B, C)[i // 2]), s) for i, s in enumerate(servers))
    tag = lambda x, y, t: f'<text class="m" x="{x}" y="{y}" font-size="16" fill="{BLUE}" text-anchor="middle">{t}</text>'
    links += tag((A[0] + B[0]) / 2, A[1] - 12, "wireguard") + tag((B[0] + C[0]) / 2, B[1] - 12, "ipsec") + tag(B[0], 136, "ospf over tunnels")
    pt = lambda *ps: "M" + " L".join(f"{x} {y}" for x, y in ps)
    routes = [(pt(servers[0], A, B, servers[3]), 4.5, 0), (pt(servers[5], C, B, A, servers[1]), 6, 1.4),
              (arc, 4, 2.6), (pt(servers[2], B, C, servers[4]), 4.5, 3.3), (f"M{C[0]} {C[1]} Q{B[0]} 60 {A[0]} {A[1]}", 4.5, 0.7)]
    pkts = "".join(f'<circle class="pkt" r="5" fill="{AMBER}" style="offset-path:path(\'{d}\');--t:{t}s;--d:-{dl}s"/>' for d, t, dl in routes)
    nodes = ""
    for p, name in zip((A, B, C), "abc"):
        nodes += (f'<rect x="{p[0] - 26}" y="{p[1] - 16}" width="52" height="32" rx="16" fill="{NAVY}" stroke="{BLUE}" stroke-width="2.5"/>'
                  f'<text class="m" x="{p[0]}" y="{p[1] + 5}" font-size="14" fill="{WHITE}" text-anchor="middle">RB</text>'
                  f'<text class="m" x="{p[0]}" y="{p[1] + 40}" font-size="17" fill="{FOG}" text-anchor="middle">mikrotik {name}</text>')
    for i, (x, y) in enumerate(servers):
        nodes += (f'<rect x="{x - 30}" y="{y}" width="60" height="40" rx="5" fill="{NAVY}" stroke="{BLUE}" stroke-width="2"/>'
                  f'<circle class="led" cx="{x + 18}" cy="{y + 12}" r="3.5" fill="{AMBER}" style="animation-delay:-{i * 0.7}s"/>'
                  f'<rect x="{x - 20}" y="{y + 24}" width="40" height="3" rx="1.5" fill="{WIRE}"/>'
                  f'<text class="m" x="{x}" y="{y + 64}" font-size="15" fill="{FOG}" text-anchor="middle">{os_names[i]}</text>')
    body = f"""{dots}
<text class="d" x="64" y="196" font-size="112" fill="{WHITE}" letter-spacing="-2">Michal</text>
<text class="d" x="64" y="306" font-size="112" fill="{WHITE}" letter-spacing="-2">Karafa</text>
<text class="b" x="66" y="372" font-size="25" fill="{FOG}">Network and infrastructure student from Slovakia.</text>
<text class="b" x="66" y="408" font-size="25" fill="{FOG}">I design, build and run networks that stay up.</text>
{links}{pkts}{nodes}"""
    return svg(W, H, body, "Michal Karafa. Network and infrastructure student from Slovakia. Diagram of three MikroTik sites linked by WireGuard and IPsec tunnels with OSPF, serving six Proxmox, Debian and Ubuntu machines.")


HOPS = [
    ("2023", "SOŠ IT Banská Bystrica", "Started the computer network technician programme, graduating 2027"),
    ("2024-05", "THR Systems, Zvolen", "First internship: CCTV, security systems, computers and networks"),
    ("2024-06", "Cisco CCNA 1", "Introduction to Networks"),
    ("2025-06", "Cisco CCNA 2", "Switching, Routing and Wireless Essentials"),
    ("2025-07", "THR Systems, Zvolen", "Summer job as IT and security systems technician"),
    ("2026", "CanSat, team TSA BB", "2nd place nationally; I ran the ground server and telemetry"),
    ("2026-05", "SWAN a.s., Banská Bystrica", "Internship at a telecom operator, on production network"),
    ("2026-05", "Erasmus+, Erfurt", "Networking side of the Lixie StopWatch project"),
    ("2026-06", "Cisco CCNA 3", "Enterprise Networking, Security and Automation. All three done"),
    ("now", "Grandify", "Lead network engineer at a VPS host: own ASN, BGP, Proxmox"),
]


def path_svg():
    W, top, row = 1280, 132, 60
    H = top + row * (len(HOPS) + 1) + 30
    body = (f'<text class="m" x="56" y="66" font-size="22" fill="{BLUE}">$ traceroute karafamichal</text>'
            f'<text class="m" x="56" y="100" font-size="18" fill="{FOG}" opacity=".7">traceroute to karafamichal, {len(HOPS) + 1} hops max, sorted by date</text>')
    for i, (when, where, what) in enumerate(HOPS):
        y = top + i * row + 34
        body += (f'<line x1="56" y1="{y - 34}" x2="{W - 56}" y2="{y - 34}" stroke="{LINE}"/>'
                 f'<text class="m" x="56" y="{y}" font-size="20" fill="{AMBER}">{i + 1:>2}</text>'
                 f'<text class="s" x="110" y="{y}" font-size="23" fill="{WHITE}">{esc(where)}</text>'
                 f'<text class="b" x="470" y="{y}" font-size="20" fill="{FOG}">{esc(what)}</text>'
                 f'<text class="m" x="{W - 56}" y="{y}" font-size="18" fill="{BLUE}" text-anchor="end">{when}</text>')
    y = top + len(HOPS) * row + 34
    body += (f'<line x1="56" y1="{y - 34}" x2="{W - 56}" y2="{y - 34}" stroke="{LINE}"/>'
             f'<text class="m" x="56" y="{y}" font-size="20" fill="{AMBER}">11</text>'
             f'<text class="m" x="110" y="{y}" font-size="20" fill="{AMBER}"><tspan class="led">*  *  *</tspan></text>'
             f'<text class="b" x="470" y="{y}" font-size="20" fill="{FOG}">MikroTik MTCNA, planned by the end of 2026</text>'
             f'<text class="m" x="{W - 56}" y="{y}" font-size="18" fill="{BLUE}" text-anchor="end">next</text>')
    alt = "My path so far: " + "; ".join(f"{w}: {a}, {b}" for w, a, b in HOPS) + "; next: MikroTik MTCNA."
    return svg(W, H, body, alt)


def planride():
    """Plan&Ride as an amber LED departure board, like the ones at Slovak bus stops."""
    W, H = 1280, 348
    led = 'fill="%s" filter="url(#glow)"' % AMBER
    rows = [("Live departures", "every stop"), ("Connection planner", "door to door"), ("Bus tracking", "on the map")]
    body = (f'<defs><filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="2.2" result="b"/>'
            f'<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
            f'<rect x="40" y="40" width="{W - 80}" height="268" rx="10" fill="#0D131D" stroke="{LINE}" stroke-width="2"/>'
            f'<text class="x" x="80" y="112" font-size="58" {led}>Plan&amp;Ride</text>'
            f'<text class="m" x="{W - 80}" y="104" font-size="20" fill="{BLUE}" text-anchor="end">par.karafa.net</text>'
            f'<line x1="80" y1="138" x2="{W - 80}" y2="138" stroke="{LINE}" stroke-width="2"/>')
    for i, (what, where) in enumerate(rows):
        y = 186 + i * 46
        body += (f'<text class="x" x="80" y="{y}" font-size="34" {led}>{what}</text>'
                 f'<text class="x" x="620" y="{y}" font-size="34" {led} opacity=".55">{where}</text>'
                 f'<text class="x led" x="{W - 80}" y="{y}" font-size="34" {led} text-anchor="end" style="animation-delay:-{i * 0.8}s">now</text>')
    return svg(W, H, body, "Plan&Ride, a free open-source app for Slovak buses: live departures, connection planner and bus tracking. par.karafa.net")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero(), encoding="utf-8")
    (OUT / "planride.svg").write_text(planride(), encoding="utf-8")
    (OUT / "path.svg").write_text(path_svg(), encoding="utf-8")
    for f in OUT.glob("*.svg"):
        assert f.read_text(encoding="utf-8").count("base64,") >= 3, f
        print(f.name, f.stat().st_size // 1024, "KB")
