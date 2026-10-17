import sqlite3
from decimal import Decimal

import pytest

from acta import exportar_csv, salas, tablero
from acta.escribir import escribir_evento
from acta.estado import estado_publico, facturas_por_estado
from acta.verificar import verificar_cadena


def test_ac1_1_numeros_consecutivos(almacen, sala):
    assert [f.num for f in almacen.filas(sala)] == [1, 2, 3, 4, 5, 6]


def test_ac1_2_no_se_modifica_ni_borra(almacen, sala):
    c = sqlite3.connect(almacen.ruta)
    with pytest.raises(sqlite3.DatabaseError, match="solo añadir"):
        c.execute("UPDATE acta SET actor='x' WHERE sala_id=?", (sala,))
    with pytest.raises(sqlite3.DatabaseError, match="solo añadir"):
        c.execute("DELETE FROM acta WHERE sala_id=?", (sala,))


def test_ac1_3_tipo_no_permitido(almacen, sala):
    with pytest.raises(ValueError):
        escribir_evento(almacen, sala, "OTRO", None, {}, "x")


def test_ac1_4_idempotencia(almacen, sala):
    a = escribir_evento(almacen, sala, "REVISION_CONCILIACION", None, {"alerta": 1}, "x")
    b = escribir_evento(almacen, sala, "REVISION_CONCILIACION", None, {"alerta": 1}, "x")
    assert a.num == b.num and len(almacen.filas(sala)) == 7


def test_ac2_3_cadena_correcta_y_alterada(almacen, sala):
    assert verificar_cadena(almacen, sala).correcta
    c = sqlite3.connect(almacen.ruta)
    c.executescript("DROP TRIGGER acta_no_modifica;")      # alguien con permisos manipula una fila
    c.execute("UPDATE acta SET actor='Otro' WHERE sala_id=? AND num=3", (sala,))
    c.commit()
    r = verificar_cadena(almacen, sala)
    assert not r.correcta and r.primera_fila_mala == 3


def test_ac4_3_estado_publico_lista_cerrada(almacen, sala):
    for f in facturas_por_estado(almacen.filas(sala)).values():
        assert estado_publico(f) in {"en revisión", "resuelta"}


def test_ac5_5_formulas_neutralizadas():
    assert exportar_csv.seguro("=1+1") == "'=1+1"
    assert all(exportar_csv.seguro(x).startswith("'") for x in ("+cmd", "-2", "@x"))
    assert exportar_csv.seguro("normal") == "normal"


def test_ac5_4_csv_con_bom_y_ac5_7_determinista(almacen, sala):
    filas = almacen.filas(sala)
    a = exportar_csv.exportar_facturas(filas)
    assert a.startswith(b"\xef\xbb\xbf") and a == exportar_csv.exportar_facturas(filas)


def test_ac6_1_cifras_con_decimal(almacen, sala):
    c = tablero.cifras(almacen.filas(sala))
    assert (c.pagadas, c.frenadas, c.pendientes) == (2, 1, 3)
    assert c.gasto == Decimal("4605900.00")          # 2.400.000 + 540 USD a 4.085 (supuesto)


def test_ac6_3_tablero_csv_y_acta_coinciden(almacen, sala):
    assert tablero.comprobar_consistencia(almacen.filas(sala))


def test_ac7_1_una_sala_no_lee_a_otra(almacen):
    a, b = salas.crear(almacen), salas.crear(almacen)
    escribir_evento(almacen, a, "REVISION_CONCILIACION", None, {"x": 1}, "x")
    assert len(almacen.filas(a)) == 7 and len(almacen.filas(b)) == 6
    assert verificar_cadena(almacen, a).correcta and verificar_cadena(almacen, b).correcta


def test_codigo_de_sala():
    assert salas.codigo_valido("7TCMN7RB")
    assert not salas.codigo_valido("../etc") and not salas.codigo_valido(None)


def test_pd1_3_la_base_va_al_volumen_de_railway(monkeypatch, tmp_path):
    from acta.almacen import AlmacenSqlite, ruta_de_la_base
    monkeypatch.delenv("ACTA_DB", raising=False)
    monkeypatch.setenv("RAILWAY_VOLUME_MOUNT_PATH", str(tmp_path))
    assert ruta_de_la_base() == str(tmp_path / "acta.db")
    assert AlmacenSqlite().ruta == str(tmp_path / "acta.db")
    monkeypatch.setenv("ACTA_DB", str(tmp_path / "otra.db"))                  # ACTA_DB manda
    assert ruta_de_la_base() == str(tmp_path / "otra.db")


def test_pd1_5_fecha_demo_fija_el_hoy(monkeypatch):
    from datetime import date
    from engine.reglas_io import hoy_bogota
    monkeypatch.setenv("FECHA_DEMO", "2026-10-17")
    assert hoy_bogota() == date(2026, 10, 17)
    monkeypatch.setenv("FECHA_DEMO", "no es fecha")                           # inválida: usa la real
    assert isinstance(hoy_bogota(), date)


def test_pd1_6_varios_visitantes_a_la_vez(almacen):
    import threading
    from acta import salas
    from acta.verificar import verificar_cadena
    from agents import flujo
    errores, creadas = [], []

    def visitante():
        try:
            s = salas.crear(almacen)
            flujo.recibir_ejemplo(almacen, s, "normal")
            creadas.append(s)
        except Exception as e:
            errores.append(e)
    hilos = [threading.Thread(target=visitante) for _ in range(6)]
    [h.start() for h in hilos]
    [h.join() for h in hilos]
    assert errores == [] and all(verificar_cadena(almacen, s).correcta for s in creadas)
