"""Almacén SQLite del acta. Toda consulta recibe la sala (AC7.1)."""
import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

RUTA_ESQUEMA = Path(__file__).with_name("esquema_sqlite.sql")
RUTA_POR_DEFECTO = Path(__file__).resolve().parent.parent / "data" / "acta_local.db"


@dataclass
class Fila:
    sala_id: str
    num: int
    tipo: str
    factura_id: str | None
    payload: dict
    actor: str
    clave_idem: str
    huella_anterior: str
    huella: str
    creado_en: str


def _a_fila(r) -> Fila:
    return Fila(r["sala_id"], r["num"], r["tipo"], r["factura_id"], json.loads(r["payload"]),
                r["actor"], r["clave_idem"], r["huella_anterior"], r["huella"], r["creado_en"])


class AlmacenSqlite:
    def __init__(self, ruta=None):
        self.ruta = str(ruta or os.environ.get("ACTA_DB") or RUTA_POR_DEFECTO)
        Path(self.ruta).parent.mkdir(parents=True, exist_ok=True)
        with self._conectar() as c:
            c.executescript(RUTA_ESQUEMA.read_text(encoding="utf-8"))

    def _conectar(self):
        c = sqlite3.connect(self.ruta, timeout=10, isolation_level=None)
        c.row_factory = sqlite3.Row
        return c

    @contextmanager
    def transaccion(self):
        """Bloqueo de escritura (BEGIN IMMEDIATE): evita números repetidos (AC1.6)."""
        c = self._conectar()
        try:
            c.execute("BEGIN IMMEDIATE")
            yield c
            c.execute("COMMIT")
        except BaseException:
            c.execute("ROLLBACK") if c.in_transaction else None
            raise
        finally:
            c.close()

    def buscar_por_clave(self, c, sala_id, clave):
        r = c.execute("SELECT * FROM acta WHERE sala_id=? AND clave_idem=?", (sala_id, clave)).fetchone()
        return _a_fila(r) if r else None

    def ultima_fila(self, c, sala_id):
        r = c.execute("SELECT * FROM acta WHERE sala_id=? ORDER BY num DESC LIMIT 1", (sala_id,)).fetchone()
        return _a_fila(r) if r else None

    def insertar(self, c, f: Fila):
        c.execute("INSERT INTO acta VALUES (?,?,?,?,?,?,?,?,?,?)",
                  (f.sala_id, f.num, f.tipo, f.factura_id,
                   json.dumps(f.payload, sort_keys=True, ensure_ascii=False),
                   f.actor, f.clave_idem, f.huella_anterior, f.huella, f.creado_en))

    def filas(self, sala_id) -> list[Fila]:
        c = self._conectar()
        try:
            return [_a_fila(r) for r in
                    c.execute("SELECT * FROM acta WHERE sala_id=? ORDER BY num", (sala_id,))]
        finally:
            c.close()

    def sala_existe(self, sala_id) -> bool:
        c = self._conectar()
        try:
            return c.execute("SELECT 1 FROM acta WHERE sala_id=? LIMIT 1", (sala_id,)).fetchone() is not None
        finally:
            c.close()
