"""PDF-Export (fpdf2, Kernschriften): Einstellungen, Ergebnis der drei Verfahren und des Optimums, Rundwege. Kein Gedankenstrich und kein Euro-Zeichen (Kernschriften)."""

from fpdf import FPDF

import apx_constants as C
import apx_evaluation as ev


def _text(value: str) -> str:
    """Zeichen, die die Kernschriften nicht kennen, ersetzen (Gedankenstrich, Pfeile, Fettdruck-Markierung, mathematische Zeichen)."""
    table = {"–": "-", "—": "-", "→": "->", "**": "", "€": "EUR", "·": "*", "³": "^3", "≤": "<=", "≥": ">=", "ρ": "rho", "−": "-", "×": "x", "„": '"', "“": '"', "⇔": "<=>"}
    for old, new in table.items():
        value = value.replace(old, new)
    return value


def _para(pdf: FPDF, height: float, text: str) -> None:
    """Absatz über die volle Breite; danach steht der Cursor wieder am linken Rand (fpdf2 setzt ihn sonst an den rechten Rand)."""
    pdf.multi_cell(0, height, _text(text), new_x="LMARGIN", new_y="NEXT")


def build_pdf(a: ev.Analysis) -> bytes:
    s = a.settings
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _text("Approximation und ihre Grenze"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _para(pdf, 5.5, f"Punkte: {s.n}   Verteilung: {C.FAMILIES[s.family]}   Zufalls-Seed: {s.seed}")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Ergebnis", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    _para(pdf, 5.5, ev.verdict_run(a)[1])
    _para(pdf, 5.5, ev.verdict_proof(a)[1])
    _para(pdf, 5.5, f"Held-Karp: {ev.fmt_int(a.opt.cells)} Tabellenzellen.")
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Rundwege", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for name, tour in (("Optimum", a.opt.tour), ("MST-Verdopplung", a.dt.tour), ("Christofides", a.chr.tour), ("nächster Nachbar", a.nn[0])):
        _para(pdf, 4.8, f"{name}: " + " -> ".join(str(v) for v in list(tour) + [tour[0]]))
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 7, "Punkte", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for i, (x, y) in enumerate(a.points):
        _para(pdf, 4.8, f"Punkt {i}: x = {x}, y = {y}")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    _para(pdf, 4.5, "Aufwand in Tabellenzellen und Zuständen, nicht in Sekunden. Sebastian Hanisch - Operations Research und Machine Learning.")
    return bytes(pdf.output())
