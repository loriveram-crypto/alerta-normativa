"""
Parser universal con navegador real (Playwright), porque varios sitios
.gov.co bloquean peticiones simples (requests/curl) aunque el contenido
no dependa de JavaScript.

Estrategias en orden (la primera que encuentre algo, gana):
  1. _estrategia_lista_con_fecha: la general, cubre Decretos, Leyes,
     Resoluciones y Agenda Regulatoria (busca fecha en el link o en su
     bloque contenedor).
  2. _estrategia_pdfs: respaldo para Minhacienda (enlaces a PDF).
  3. _estrategia_generica: último respaldo, sin fecha.
"""
from playwright.sync_api import sync_playwright
from date_utils import extraer_fecha

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _estrategia_lista_con_fecha(page, url_base: str) -> list[dict]:
    items = []
    vistos = set()
    enlaces = page.query_selector_all("a")

    for a in enlaces:
        titulo = (a.inner_text() or "").strip()
        href = a.get_attribute("href") or ""
        if not titulo or len(titulo) < 8:
            continue

        try:
            texto_contenedor = a.evaluate(
                "el => (el.closest('li') || el.parentElement || el).innerText"
            )
        except Exception:
            texto_contenedor = titulo

        fecha = extraer_fecha(texto_contenedor) or extraer_fecha(titulo)
        if not fecha:
            continue

        clave = href or titulo
        if clave in vistos:
            continue
        vistos.add(clave)

        if href:
            link = href if href.startswith("http") else url_base.rstrip("/") + "/" + href.lstrip("/")
        else:
            link = url_base

        items.append({"titulo": titulo, "link": link, "fecha": fecha})

    return items


def _estrategia_pdfs(page, url_base: str) -> list[dict]:
    items = []
    enlaces = page.query_selector_all("a[href*='.pdf']")
    vistos = set()

    for a in enlaces:
        href = a.get_attribute("href") or ""
        titulo = (a.inner_text() or "").strip()
        if not titulo or not href or href in vistos:
            continue
        vistos.add(href)

        fecha = ""
        try:
            texto_siguiente = a.evaluate(
                "el => { let sib = el.parentElement ? el.parentElement.nextElementSibling : null; "
                "return sib ? sib.innerText : ''; }"
            )
            fecha = extraer_fecha(texto_siguiente or "")
        except Exception:
            pass

        link = href if href.startswith("http") else url_base.rstrip("/") + "/" + href.lstrip("/")
        items.append({"titulo": titulo, "link": link, "fecha": fecha})

    return items


def _estrategia_generica(page) -> list[dict]:
    items = []
    enlaces = page.query_selector_all("main a, #content a, .content a, article a, body a")
    for a in enlaces:
        titulo = (a.inner_text() or "").strip()
        href = a.get_attribute("href") or ""
        if titulo and len(titulo) > 20 and href:
            items.append({"titulo": titulo, "link": href, "fecha": ""})
    return items


def obtener_items(url: str) -> list[dict]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=USER_AGENT)

        try:
            page.goto(url, wait_until="networkidle", timeout=45000)
        except Exception as e:
            print(f"  ⚠️ Error de navegación en {url}: {e}")

        page.wait_for_timeout(2000)

        items = _estrategia_lista_con_fecha(page, url)
        if not items:
            items = _estrategia_pdfs(page, url)
        if not items:
            items = _estrategia_generica(page)

        browser.close()
        return items
