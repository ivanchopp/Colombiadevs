"""Estado de entrada de cada factura. No es el acta: aquí vive el chat y el texto libre (EA1.4, EA7)."""
import json
import sqlite3
from datetime import datetime, timezone

ESQUEMA = """
CREATE TABLE IF NOT EXISTS entrada (
  sala_id TEXT NOT NULL, factura_id TEXT NOT NULL, estado TEXT NOT NULL, turnos INTEGER NOT NULL DEFAULT 0,
  pendientes TEXT NOT NULL, lectura TEXT NOT NULL, aclarados TEXT NOT NULL, chat TEXT NOT NULL,
  texto TEXT, nombre TEXT NOT NULL, tipo TEXT NOT NULL, orden_en_texto INTEGER NOT NULL DEFAULT 0,
  modo TEXT NOT NULL, segunda TEXT NOT NULL, creado TEXT NOT NULL,
  PRIMARY KEY (sala_id, factura_id)
)"""
JSON = ("pendientes", "lectura", "aclarados", "chat")


class EstadoEntrada:
    def __init__(self, almacen):
        self.ruta = almacen.ruta
        with self._c() as c:
            c.execute(ESQUEMA)

    def _c(self):
        c = sqlite3.connect(self.ruta, timeout=10)
        c.row_factory = sqlite3.Row
        return c

    @staticmethod
    def _fila(r):
        d = dict(r)
        for k in JSON:
            d[k] = json.loads(d[k])
        d["orden_en_texto"] = bool(d["orden_en_texto"])
        return d

    def crear(self, sala_id, factura_id, **campos):
        d = dict(turnos=0, texto=None, orden_en_texto=0, creado=datetime.now(timezone.utc).isoformat())
        d.update(campos)
        d["orden_en_texto"] = int(d["orden_en_texto"])
        for k in JSON:
            d[k] = json.dumps(d[k], ensure_ascii=False, default=str)
        cols = ["sala_id", "factura_id"] + list(d)
        with self._c() as c:
            c.execute(f"INSERT INTO entrada ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                      [sala_id, factura_id, *d.values()])

    def obtener(self, sala_id, factura_id):
        with self._c() as c:
            r = c.execute("SELECT * FROM entrada WHERE sala_id=? AND factura_id=?", (sala_id, factura_id)).fetchone()
        return self._fila(r) if r else None

    def listar(self, sala_id):
        with self._c() as c:
            return [self._fila(r) for r in c.execute(
                "SELECT * FROM entrada WHERE sala_id=? ORDER BY creado", (sala_id,))]

    def actualizar(self, sala_id, factura_id, **campos):
        for k in JSON:
            if k in campos:
                campos[k] = json.dumps(campos[k], ensure_ascii=False, default=str)
        if "orden_en_texto" in campos:
            campos["orden_en_texto"] = int(campos["orden_en_texto"])
        sets = ", ".join(f"{k}=?" for k in campos)
        with self._c() as c:
            c.execute(f"UPDATE entrada SET {sets} WHERE sala_id=? AND factura_id=?",
                      [*campos.values(), sala_id, factura_id])
