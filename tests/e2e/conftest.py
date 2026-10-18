"""Pruebas de extremo a extremo (navegador real). Se activan con E2E=1 y necesitan `pip install playwright`
y un Chromium (en la sesión de la nube: /opt/pw-browsers/chromium).

Por defecto arrancan la app en local, en modo demo (sin clave de IA, sin costo) y con la fecha fija.
Con E2E_URL=https://... se prueba un despliegue ya publicado; ahí solo se corren las pruebas de solo lectura."""
import os
import re
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent.parent
URL_EXTERNA = os.environ.get("E2E_URL", "").rstrip("/")

if os.environ.get("E2E") != "1" and not URL_EXTERNA:
    collect_ignore_glob = ["test_*.py"]                      # sin E2E=1 no se recogen (la suite normal no los corre)


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def base_url(tmp_path_factory):
    if URL_EXTERNA:
        yield URL_EXTERNA
        return
    puerto = _puerto_libre()
    entorno = {"PATH": os.environ["PATH"], "HOME": os.environ.get("HOME", "/tmp"),
               "ACTA_DB": str(tmp_path_factory.mktemp("e2e") / "acta.db"), "FECHA_DEMO": "2026-10-17",
               "ENTRADA_MODO": "demo"}                        # modo demo: sin IA, sin costo, resultado estable
    log = (tmp_path_factory.mktemp("log") / "streamlit.log").open("w")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", str(RAIZ / "app" / "Envía_facturas.py"), "--server.headless=true",
         f"--server.port={puerto}", "--server.address=127.0.0.1"], cwd=RAIZ, env=entorno, stdout=log, stderr=log)
    url = f"http://127.0.0.1:{puerto}"
    try:
        for _ in range(60):
            try:
                if urllib.request.urlopen(f"{url}/_stcore/health", timeout=2).read().strip() == b"ok":
                    break
            except OSError:
                time.sleep(1)
        else:
            pytest.fail("La app no arrancó en 60 s")
        yield url
    finally:
        proc.terminate()
        proc.wait(timeout=15)


@pytest.fixture(scope="session")
def navegador():
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    ruta = os.environ.get("CHROMIUM_PATH") or next(
        (str(p) for p in (Path("/opt/pw-browsers/chromium"),) if p.exists()), None)
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=ruta) if ruta else p.chromium.launch()
        yield nav
        nav.close()


@pytest.fixture
def pagina(navegador):
    contexto = navegador.new_context(viewport={"width": 1300, "height": 1600}, accept_downloads=True)
    contexto.set_default_timeout(30_000)
    pg = contexto.new_page()
    yield pg
    contexto.close()


class Sala:
    """Una sala nueva y atajos para recorrer la app."""

    def __init__(self, pg, base):
        self.pg, self.base = pg, base
        pg.goto(base)
        pg.wait_for_url("**sala=*")
        self.codigo = pg.url.split("sala=")[1].split("&")[0]
        pg.get_by_text("Envía una factura").wait_for()

    def ir(self, ruta: str):
        self.pg.goto(f"{self.base}/{ruta}?sala={self.codigo}")
        self.pg.get_by_text("Entrar como").wait_for()
        self.pg.wait_for_timeout(2000)                          # Streamlit dibuja la página por partes

    def texto(self) -> str:
        return self.pg.inner_text("body")

    def rol(self, nombre: str):
        self.pg.get_by_role("radio", name=re.compile(nombre)).click()
        self.pg.wait_for_timeout(1500)

    def subir(self, archivo: str):
        pg = self.pg
        pg.set_input_files("input[type=file]", str(RAIZ / "data" / "facturas_ejemplo" / archivo))
        pg.get_by_role("button", name="Enviar esta factura").click()
        pg.get_by_text("Gracias.").first.wait_for()


@pytest.fixture
def sala(pagina, base_url):
    return Sala(pagina, base_url)
