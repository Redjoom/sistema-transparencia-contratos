import fitz
from . import pii_detector

LEGEND = (
    "La presente versión pública fue elaborada de conformidad a los "
    "“Lineamientos Generales de Clasificación y Desclasificación de la "
    "Información, así como para la elaboración de versiones públicas”, "
    "con lo establecido en los artículos 11 fracción VI, 98 fracción III "
    "y 113 fracción I de la Ley Federal de Transparencia y Acceso a la "
    "Información Pública y 24 fracción VI y 116 de la Ley General de "
    "Transparencia y Acceso a la Información Pública, así como 17, 18, "
    "22, 25, 32 y demás relativos de la Ley General de Protección de "
    "Datos Personales en Posesión de Sujetos Obligados y aprobada por "
    "el Comité de Transparencia de la Comisión Ejecutiva de Atención "
    "a Víctimas, al ser de carácter confidencial por contener datos "
    "personales de personas identificadas o identificables."
)


def find_pii_in_pages(pages):
    page_matches = {}
    for p in pages:
        matches = pii_detector.detect(p["text"])
        if matches:
            page_matches[p["number"]] = matches
    return page_matches


def _find_line_number(page, y_center):
    blocks = page.get_text("blocks")
    best = None
    best_dist = float("inf")
    for i, b in enumerate(blocks):
        by = (b[1] + b[3]) / 2
        dist = abs(by - y_center)
        if dist < best_dist:
            best_dist = dist
            best = i + 1
    return best if best else 0


def apply_redaction(page, matches):
    info = []
    for m in matches:
        text_instances = page.search_for(m["text"])
        for inst in text_instances:
            h = inst.y1 - inst.y0
            shrink = h * 0.10
            adj = fitz.Rect(inst.x0, inst.y0 + shrink, inst.x1, inst.y1 - shrink)
            page.add_redact_annot(adj, fill=(0, 0, 0), text="[REDACTADO]")
            y_center = (inst.y0 + inst.y1) / 2
            info.append({
                "rect": inst,
                "label": m["label"],
                "text": m["text"],
                "line": _find_line_number(page, y_center),
            })
    page.apply_redactions()
    return info


FOOTER_FONT_SIZE = 7


def _draw_footer(page, page_num, info, pw, ph):
    if not info:
        return
    counts = {}
    for it in info:
        counts[it["label"]] = counts.get(it["label"], 0) + 1
    parts = [f"{k}({v})" for k, v in sorted(counts.items())]
    summary = f"VP Pág.{page_num} — " + ", ".join(parts)

    x0 = 36
    y0 = ph - 22
    page.draw_line(
        fitz.Point(x0, y0), fitz.Point(pw - x0, y0),
        color=(0.5, 0.5, 0.5), width=0.3,
    )
    page.insert_text(
        fitz.Point(x0 + 2, y0 + 10),
        summary, fontname="helv", fontsize=6,
    )


def _draw_legend_page(doc, pw, ph):
    page = doc.new_page(width=pw, height=ph)
    margin = 36
    y = margin + 20
    page.insert_textbox(
        fitz.Rect(margin, y, pw - margin, ph - margin),
        "LEYENDA DE PROTECCIÓN DE DATOS\n\n" + LEGEND,
        fontname="helv", fontsize=9, align=0,
    )


def post_process(doc, per_page_info):
    pw = doc[0].rect.width if doc else 612
    ph = doc[0].rect.height if doc else 792
    for i in range(len(doc)):
        page = doc[i]
        pn = i + 1
        page_info = per_page_info.get(pn, [])
        if page_info:
            _draw_footer(page, pn, page_info, pw, ph)
    _draw_legend_page(doc, pw, ph)
