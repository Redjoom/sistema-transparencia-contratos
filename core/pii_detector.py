import re


PATTERNS = {
    "CURP": re.compile(
        r"[A-Z][AEIOU][A-Z]{2}\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])"
        r"[HM](?:AS|BC|BS|CC|CL|CM|CS|CH|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS|NE)"
        r"[B-DF-HJ-NP-TV-Z]{3}[A-Z0-9]\d"
    ),
    "RFC": re.compile(
        r"[A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3}"
    ),
    "EMAIL": re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    ),
    "PHONE_MX": re.compile(
        r"\b(?:\+?52)?[\s-]?(?:\d{2,3})?[\s-]?\d{2,3}[\s-]?\d{4}[\s-]?\d{4}\b"
    ),
    "INE": re.compile(
        r"\b\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])"  # fecha
        r"(?:[A-Z]{2})\d{5}\b"  # dos letras + 5 dígitos
    ),
    "CREDIT_CARD": re.compile(
        r"\b(?:\d[ -]*?){13,19}\b"
    ),
    "BANK_ACCOUNT": re.compile(
        r"\b\d{16,18}\b"
    ),
    "SOCIAL_SECURITY": re.compile(
        r"\b\d{11}\b"
    ),
    "PASSPORT": re.compile(
        r"\b[A-Z]\d{8}\b"
    ),
    "PROFESSIONAL_ID": re.compile(
        r"\b\d{5,8}\b"
    ),
}

LABELS = {
    "CURP": "CURP",
    "RFC": "RFC",
    "EMAIL": "Correo electrónico",
    "PHONE_MX": "Teléfono",
    "INE": "INE/IFE",
    "CREDIT_CARD": "Tarjeta bancaria",
    "BANK_ACCOUNT": "Cuenta bancaria",
    "SOCIAL_SECURITY": "NSS",
    "PASSPORT": "Pasaporte",
    "PROFESSIONAL_ID": "Cédula profesional",
}


TYPE_PRIORITY = [
    "CURP", "RFC", "EMAIL", "INE", "CREDIT_CARD", "PHONE_MX",
    "PASSPORT", "SOCIAL_SECURITY", "PROFESSIONAL_ID", "BANK_ACCOUNT",
]


def detect(text):
    raw = []
    for name, pattern in PATTERNS.items():
        for m in pattern.finditer(text):
            raw.append({
                "type": name,
                "label": LABELS.get(name, name),
                "text": m.group(),
                "start": m.start(),
                "end": m.end(),
            })
    raw.sort(key=lambda r: (r["start"], -r["end"]))

    merged = []
    for m in raw:
        if merged and m["start"] < merged[-1]["end"]:
            prev = merged[-1]
            if (m["end"] - m["start"]) > (prev["end"] - prev["start"]):
                merged[-1] = m
            elif (m["end"] - m["start"]) == (prev["end"] - prev["start"]):
                if TYPE_PRIORITY.index(m["type"]) < TYPE_PRIORITY.index(prev["type"]):
                    merged[-1] = m
        else:
            merged.append(m)

    return merged


def redact_text(text, matches, replacement="[REDACTADO]"):
    result = text
    for m in reversed(matches):
        result = result[:m["start"]] + replacement + result[m["end"]:]
    return result
