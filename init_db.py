"""Crea el esquema del acta (idempotente). SQLite en local; PostgreSQL pendiente de probar."""
import os
import sqlite3
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent


def main() -> int:
    url = os.environ.get("DATABASE_URL", "sqlite:///colombiadevs.db")
    if not url.startswith("sqlite"):
        print("AVISO: PostgreSQL aún no está implementado (tarea PT12); no se creó nada.")
        return 0
    ruta = url.removeprefix("sqlite:///")
    con = sqlite3.connect(ruta)
    con.executescript((RAIZ / "acta" / "esquema_sqlite.sql").read_text(encoding="utf-8"))
    con.close()
    print(f"Base lista: {ruta}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
