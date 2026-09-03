"""
Minimal SVG drawing helpers for the project diagrams.

Everything is monospace on purpose: DejaVu Sans Mono has a fixed advance width of
0.60238 em, so text width is exactly computable and boxes can be sized from their
content. That is what keeps labels from overflowing their boxes or colliding with
arrowheads -- the two failure modes of the hand-written SVGs in the source document.

Palette is dark-mode native: the diagrams are drawn on a dark canvas with light
strokes, which is how they are read in practice (GitHub dark).
"""

# --- palette ---------------------------------------------------------------
BG = "#0d1117"          # canvas
PANEL = "#161b22"       # box fill
PANEL_2 = "#1c2129"     # nested / alternate box fill
EDGE = "#30363d"        # neutral border
GRID = "#21262d"        # grid dots, faint rules
FG = "#e6edf3"          # primary text
FG_DIM = "#9198a1"      # secondary text
FG_FAINT = "#6e7681"    # captions inside figures

# Wire colour code, carried over from the source document
# (yellow +12V / copper +5V / red +3.3V / grey GND / blue signal)
V12 = "#e3b341"
V5 = "#f0883e"
V33 = "#ff7b72"
GND = "#8b949e"
SIG = "#58a6ff"
RADIO = "#56d4dd"

NODE_A = "#7ee787"      # locking node
NODE_B = "#d2a8ff"      # gauge node
NODE_C = "#f778ba"      # analogue front end
WARN = "#f0883e"

MONO = "'DejaVu Sans Mono','Liberation Mono',ui-monospace,Menlo,Consolas,monospace"
ADV = 0.60238           # advance width per em for DejaVu Sans Mono


def tw(text: str, size: float) -> float:
    """Exact rendered width of `text` at `size` px in DejaVu Sans Mono."""
    return len(text) * size * ADV


class Svg:
    def __init__(self, w, h, bg=BG):
        self.w, self.h = w, h
        self.parts = []
        self.bg = bg

    def add(self, s):
        self.parts.append(s)
        return self

    # -- primitives ---------------------------------------------------------
    def rect(self, x, y, w, h, fill=PANEL, stroke=EDGE, sw=1.4, r=8, dash=None, op=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{op}"' if op is not None else ""
        return self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}/>'
        )

    def line(self, x1, y1, x2, y2, stroke=EDGE, sw=1.6, dash=None, cap="round", marker=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = f' marker-end="url(#{marker})"' if marker else ""
        return self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-linecap="{cap}"{d}{m}/>'
        )

    def poly(self, pts, stroke=EDGE, sw=1.6, marker=None, dash=None):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        m = f' marker-end="url(#{marker})"' if marker else ""
        d = f' stroke-dasharray="{dash}"' if dash else ""
        return self.add(
            f'<polyline points="{p}" fill="none" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"{d}{m}/>'
        )

    def dot(self, x, y, r=3.4, fill=None):
        return self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}"/>')

    def text(self, x, y, s, size=13, fill=FG, anchor="start", weight=400, opacity=1.0):
        esc = (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        return self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" font-family="{MONO}" font-size="{size}" '
            f'font-weight="{weight}" fill="{fill}" text-anchor="{anchor}" '
            f'opacity="{opacity}" xml:space="preserve">{esc}</text>'
        )

    # -- composites ---------------------------------------------------------
    def label_box(self, x, y, text, size=12, fill=PANEL_2, stroke=EDGE, color=FG,
                  padx=9, pady=6, r=6, anchor="left"):
        """A pill sized exactly to its text. Returns (x, y, w, h)."""
        w = tw(text, size) + 2 * padx
        h = size + 2 * pady + 2
        if anchor == "center":
            x = x - w / 2
        elif anchor == "right":
            x = x - w
        self.rect(x, y, w, h, fill=fill, stroke=stroke, r=r)
        self.text(x + w / 2, y + h / 2 + size * 0.36, text, size=size, fill=color, anchor="middle")
        return (x, y, w, h)

    def card(self, x, y, w, title, lines, accent=EDGE, title_size=14, line_size=12,
             fill=PANEL, pad=14, gap=6, title_gap=10, title_color=None):
        """Titled box with body lines. Height is derived from the content."""
        h = pad + title_size + title_gap + len(lines) * (line_size + gap) - gap + pad
        self.rect(x, y, w, h, fill=fill, stroke=accent, sw=1.8, r=10)
        cy = y + pad + title_size * 0.82
        self.text(x + pad, cy, title, size=title_size,
                  fill=title_color or accent, weight=700)
        cy += title_gap + line_size * 0.2
        for ln in lines:
            cy += line_size + gap
            self.text(x + pad, cy, ln, size=line_size, fill=FG_DIM)
        return (x, y, w, h)

    def caption(self, y, text, size=12):
        return self.text(self.w / 2, y, text, size=size, fill=FG_FAINT, anchor="middle")

    # -- output -------------------------------------------------------------
    def render(self):
        defs = f"""<defs>
  <marker id="arw" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1.2 L9.5,5 L0,8.8 z" fill="{FG_DIM}"/></marker>
  <marker id="arw_sig" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1.2 L9.5,5 L0,8.8 z" fill="{SIG}"/></marker>
  <marker id="arw_radio" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1.2 L9.5,5 L0,8.8 z" fill="{RADIO}"/></marker>
  <marker id="arw_v12" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1.2 L9.5,5 L0,8.8 z" fill="{V12}"/></marker>
  <marker id="arw_v5" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1.2 L9.5,5 L0,8.8 z" fill="{V5}"/></marker>
  <marker id="arw_gnd" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1.2 L9.5,5 L0,8.8 z" fill="{GND}"/></marker>
  <marker id="arw_a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1.2 L9.5,5 L0,8.8 z" fill="{NODE_A}"/></marker>
  <marker id="arw_c" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7"
          orient="auto-start-reverse"><path d="M0,1.2 L9.5,5 L0,8.8 z" fill="{NODE_C}"/></marker>
</defs>"""
        body = "\n".join(self.parts)
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" '
            f'width="{self.w}" height="{self.h}">\n{defs}\n'
            f'<rect x="0" y="0" width="{self.w}" height="{self.h}" fill="{self.bg}"/>\n'
            f"{body}\n</svg>\n"
        )


MARKER = {V12: "arw_v12", V5: "arw_v5", SIG: "arw_sig", GND: "arw_gnd",
          RADIO: "arw_radio", NODE_A: "arw_a", NODE_C: "arw_c",
          FG_DIM: "arw", EDGE: "arw"}


def marker_for(color):
    return MARKER.get(color, "arw")
