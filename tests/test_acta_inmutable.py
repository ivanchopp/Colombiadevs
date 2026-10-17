import sqlite3
from pathlib import Path

import pytest

ESQUEMA = Path(__file__).resolve().parents[1] / "acta" / "esquema_sqlite.sql"


@pytest.fixture
def con():
    c = sqlite3.connect(":memory:")
    c.executescript(ESQUEMA.read_text(encoding="utf-8"))
    c.execute("INSERT INTO acta VALUES ('S',1,'DECISION','F1','{}','motor','k1','a','b','2026-10-17T00:00:00Z')")
    return c


def test_no_actualiza(con):
    with pytest.raises(sqlite3.DatabaseError, match="solo añadir"):
        con.execute("UPDATE acta SET actor='x'")


def test_no_borra(con):
    with pytest.raises(sqlite3.DatabaseError, match="solo añadir"):
        con.execute("DELETE FROM acta")


def test_idempotencia(con):
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO acta VALUES ('S',2,'DECISION','F1','{}','motor','k1','b','c','2026-10-17T00:00:00Z')")


def test_tipo_invalido(con):
    with pytest.raises(sqlite3.IntegrityError):
        con.execute("INSERT INTO acta VALUES ('S',2,'OTRO','F1','{}','motor','k2','b','c','2026-10-17T00:00:00Z')")
