"""
Vigilancia normativa - script principal.

Flujo:
  1. Lee sitios.yaml
  2. Para cada sitio, obtiene los items actuales (Playwright)
  3. Compara contra estado.json (lo visto en la corrida anterior)
  4. Los items nuevos se agregan a data/normativa.xlsx
  5. Guarda estado.json actualizado

GitHub Actions corre esto por horario y hace commit de los cambios
(estado.json y data/normativa.xlsx) de vuelta al repositorio.
"""
import json
import hashlib
import sys
from pathlib import Path

import yaml

from parsers import dinamico as parser
from excel_writer import agregar_filas

RUTA_SITIOS = Path(__file__).parent / "sitios.yaml"
RUTA_ESTADO = Path(__file__).parent / "estado.json"


def cargar_sitios() -> list[dict]:
    with open(RUTA_SITIOS, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["sitios"]


def cargar_estado() -> dict:
    if RUTA_ESTADO.exists():
        with open(RUTA_ESTADO, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_estado(estado: dict):
    with open(RUTA_ESTADO, "w", encoding="utf-8") as f:
        json.dump(estado, f, ensure_ascii=False, indent=2)


def id_unico(item: dict) -> str:
    base = f"{item.get('titulo', '')}|{item.get('link', '')}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def procesar_sitio(sitio: dict, estado: dict) -> list[dict]:
    nombre = sitio["nombre"]
    url = sitio["url"]

    print(f"Revisando: {nombre} ({url})")

    try:
        items = parser.obtener_items(url)
    except Exception as e:
        print(f"  ❌ Error al procesar {nombre}: {e}")
        return []

    vistos_previos = set(estado.get(url, []))
    nuevos = []

    for item in items:
        if not item.get("fecha"):
            continue  # sin fecha reconocible: probablemente ruido (menú, etc.)

        uid = id_unico(item)
        if uid not in vistos_previos:
            nuevos.append({**item, "entidad": nombre, "url_fuente": url})
            vistos_previos.add(uid)

    estado[url] = list(vistos_previos)

    print(f"  → {len(items)} items encontrados, {len(nuevos)} nuevos con fecha válida")
    return nuevos


def main():
    sitios = cargar_sitios()
    estado = cargar_estado()

    todos_los_nuevos = []
    for sitio in sitios:
        nuevos = procesar_sitio(sitio, estado)
        todos_los_nuevos.extend(nuevos)

    agregar_filas(todos_los_nuevos)
    guardar_estado(estado)

    if todos_los_nuevos:
        print(f"\n✅ {len(todos_los_nuevos)} novedades agregadas al Excel.")
    else:
        print("\nSin novedades en esta corrida.")


if __name__ == "__main__":
    sys.exit(main())
