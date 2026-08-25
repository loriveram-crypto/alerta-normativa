"""
Detección de fechas en español, en varios formatos reales encontrados:
  - "31 DE JULIO DE 2026"      (Decretos, Leyes)
  - "5 AGOSTO DE 2026"          (Resoluciones, sin "DE" tras el día)
  - "21 de Julio 2026"          (Agenda Regulatoria, sin "de" antes del año)
  - "agosto 11, 2026"           (Minhacienda, mes primero)
"""
import re

MESES = (
    "enero|febrero|marzo|abril|mayo|junio|julio|agosto|"
    "septiembre|octubre|noviembre|diciembre"
)

PATRON_FECHA_DIA_MES_ANIO = re.compile(
    rf"(\d{{1,2}})\s+(?:de|DE)?\s*({MESES})\s+(?:de|DE)?\s*(\d{{4}})",
    re.IGNORECASE,
)
PATRON_FECHA_MES_DIA_ANIO = re.compile(
    rf"({MESES})\s+(\d{{1,2}}),?\s+(\d{{4}})",
    re.IGNORECASE,
)


def extraer_fecha(texto: str) -> str:
    """Devuelve la fecha normalizada 'DD DE MES DE YYYY', o "" si no encuentra."""
    if not texto:
        return ""

    m = PATRON_FECHA_DIA_MES_ANIO.search(texto)
    if m:
        dia, mes, anio = m.groups()
        return f"{dia} DE {mes.upper()} DE {anio}"

    m = PATRON_FECHA_MES_DIA_ANIO.search(texto)
    if m:
        mes, dia, anio = m.groups()
        return f"{dia} DE {mes.upper()} DE {anio}"

    return ""
