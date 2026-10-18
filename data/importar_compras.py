"""Convierte el listado de proveedores del equipo (.xlsx) a data/proveedores.yaml (spec ordenes-de-compra, OT1).

Uso: python3 data/importar_compras.py <Listado_Proveedores.xlsx>

El .xlsx no se sube al repositorio (es público y trae dirección, teléfono y correo, OC1.2): solo pasan
al YAML id, nombre, país, identificación tributaria, tipo y una cuenta ficticia (OCD3). Las marcas de
identificación repetida o inválida se calculan aquí (OC1.3, OC1.4); nada se corrige en silencio.
"""
import re
import sys
from collections import Counter
from pathlib import Path

import yaml

DESTINO = Path(__file__).resolve().parent / "proveedores.yaml"
FORMATOS = {("NIT", None): r"\d{9}-\d", ("RFC", None): r"[A-Z&Ñ0-9]{12,13}",
            ("RUC", "Perú"): r"\d{11}", ("RUC", "Ecuador"): r"\d{13}"}


def formato_valido(tipo: str, pais: str, id_tributaria: str) -> bool:
    patron = FORMATOS.get((tipo, pais)) or FORMATOS.get((tipo, None))
    return bool(patron and re.fullmatch(patron, id_tributaria))


def proveedores_desde_filas(filas) -> list[dict]:
    """filas: tuplas (id, nombre, pais, id_tributaria, tipo_id, ...). Lanza ValueError si un id o nombre se repite."""
    provs = [{"id": int(f[0]), "nombre": str(f[1]).strip(), "pais": str(f[2]).strip(),
              "id_tributaria": str(f[3]).strip(), "tipo_id": str(f[4]).strip()} for f in filas]
    for campo in ("id", "nombre"):
        repetidos = [k for k, n in Counter(p[campo] for p in provs).items() if n > 1]
        if repetidos:
            raise ValueError(f"{campo} repetido en el listado: {repetidos[:5]}")
    veces = Counter(p["id_tributaria"] for p in provs)
    for p in provs:
        p["cuenta"] = f"Cuenta demo ···{p['id']:04d}"            # ficticia (OCD3)
        p["marcas"] = ([] if veces[p["id_tributaria"]] == 1 else ["identificacion_repetida"]) + \
                      ([] if formato_valido(p["tipo_id"], p["pais"], p["id_tributaria"]) else ["identificacion_invalida"])
    return sorted(provs, key=lambda p: p["id"])


def leer_xlsx(ruta) -> list[tuple]:
    import openpyxl                                              # solo para importar; no va a producción
    hoja = openpyxl.load_workbook(ruta, read_only=True, data_only=True).active
    filas = list(hoja.iter_rows(values_only=True))
    if [str(c) for c in filas[0][:5]] != ["ID_Proveedor", "Nombre", "Pais", "Identificacion_Tributaria", "Tipo_Id"]:
        raise ValueError(f"columnas inesperadas: {filas[0]}")
    return [f for f in filas[1:] if f and f[0] is not None]


def escribir(provs, origen: str):
    encabezado = ("# Proveedores de prueba (FICTICIOS, supuesto). Generado con data/importar_compras.py; no editar a mano.\n"
                  f"# Origen: {origen}. Sin dirección, teléfono ni correo (spec ordenes-de-compra, OC1.2).\n"
                  "# cuenta: ficticia (OCD3). marcas: identificacion_repetida / identificacion_invalida (OC1.3, OC1.4).\n")
    cuerpo = yaml.safe_dump({"supuesto": True, "proveedores": provs}, allow_unicode=True, sort_keys=False, width=200)
    DESTINO.write_text(encabezado + cuerpo, encoding="utf-8")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    provs = proveedores_desde_filas(leer_xlsx(sys.argv[1]))
    escribir(provs, re.sub(r"^[0-9a-f]{8}-", "", Path(sys.argv[1]).name))   # sin el prefijo de subida
    marcados = [p for p in provs if p["marcas"]]
    print(f"{len(provs)} proveedores escritos en {DESTINO.name}; {len(marcados)} con marcas.")
