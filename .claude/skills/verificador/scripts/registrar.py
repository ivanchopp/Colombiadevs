#!/usr/bin/env python3
"""Registra una verificación en .verificaciones/ y regenera VERIFICACIONES.md.

Uso:
  registrar.py --cambio "..." --veredicto APROBADO|RECHAZADO \
      [--archivos a b] [--hallazgo "SEV|categoria|archivo[:linea]|problema|correccion"]... \
      [--comprobaciones "..."] [--reemplaza VER-0001]
  registrar.py --listar
"""
import argparse, json, re, subprocess, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

SEVERIDADES = {"BLOQUEANTE", "ADVERTENCIA", "NOTA"}
CATEGORIAS = {"alcance", "convenciones", "errores", "seguridad"}


def raiz():
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return Path(r.stdout.strip()) if r.returncode == 0 else Path.cwd()


def git(*args):
    r = subprocess.run(["git", *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def cargar(carpeta):
    return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(carpeta.glob("VER-*.json"))]


def esc(t):
    return str(t).replace("|", "\\|").replace("\n", " ")


def regenerar(raiz_, entradas):
    f = ["# Verificaciones", "",
         "Historial generado por la skill `verificador`. No editar a mano: cada fila viene de `.verificaciones/VER-XXXX.json`.", "",
         "| ID | Fecha | Veredicto | Cambio | Bloqueantes | Advertencias | Commit | Reemplaza |",
         "|---|---|---|---|---|---|---|---|"]
    for e in reversed(entradas):
        h = e["hallazgos"]
        b = sum(x["severidad"] == "BLOQUEANTE" for x in h)
        a = sum(x["severidad"] == "ADVERTENCIA" for x in h)
        f.append(f"| {e['id']} | {e['fecha'][:16].replace('T', ' ')} | {e['veredicto']} | {esc(e['cambio'])} | {b} | {a} | {e['commit'][:7] or '—'} | {e.get('reemplaza') or '—'} |")
    f.append("")
    for e in reversed(entradas):
        if not e["hallazgos"]:
            continue
        f += [f"## {e['id']} — {e['veredicto']}", ""]
        for x in e["hallazgos"]:
            f.append(f"- **{x['severidad']}** ({x['categoria']}) `{x['ubicacion']}`: {x['problema']}" + (f" → {x['correccion']}" if x["correccion"] else ""))
        f.append("")
    (raiz_ / "VERIFICACIONES.md").write_text("\n".join(f), encoding="utf-8")


def parse_hallazgo(s):
    p = [x.strip() for x in s.split("|")]
    if len(p) < 4:
        sys.exit(f"Hallazgo mal formado (SEV|categoria|ubicacion|problema[|correccion]): {s}")
    sev, cat, ub, prob = p[0].upper(), p[1].lower(), p[2], p[3]
    if sev not in SEVERIDADES:
        sys.exit(f"Severidad inválida '{sev}'. Usa {sorted(SEVERIDADES)}")
    if cat not in CATEGORIAS:
        sys.exit(f"Categoría inválida '{cat}'. Usa {sorted(CATEGORIAS)}")
    return {"severidad": sev, "categoria": cat, "ubicacion": ub, "problema": prob,
            "correccion": p[4] if len(p) > 4 else ""}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cambio")
    ap.add_argument("--veredicto", choices=["APROBADO", "RECHAZADO"])
    ap.add_argument("--archivos", nargs="*", default=[])
    ap.add_argument("--hallazgo", action="append", default=[])
    ap.add_argument("--comprobaciones", default="")
    ap.add_argument("--reemplaza")
    ap.add_argument("--listar", action="store_true")
    a = ap.parse_args()

    r = raiz()
    carpeta = r / ".verificaciones"
    carpeta.mkdir(exist_ok=True)
    entradas = cargar(carpeta)

    if a.listar:
        for e in entradas:
            print(f"{e['id']}  {e['fecha'][:16]}  {e['veredicto']:<9}  {e['cambio']}")
        if not entradas:
            print("Sin verificaciones registradas.")
        return

    if not a.cambio or not a.veredicto:
        sys.exit("Faltan --cambio y --veredicto")
    hallazgos = [parse_hallazgo(h) for h in a.hallazgo]
    bloq = any(h["severidad"] == "BLOQUEANTE" for h in hallazgos)
    if bloq and a.veredicto == "APROBADO":
        sys.exit("Incoherente: hay hallazgos BLOQUEANTE, el veredicto debe ser RECHAZADO.")
    if not bloq and a.veredicto == "RECHAZADO":
        sys.exit("Incoherente: RECHAZADO requiere al menos un hallazgo BLOQUEANTE.")
    if a.reemplaza and not any(e["id"] == a.reemplaza for e in entradas):
        sys.exit(f"--reemplaza apunta a un ID inexistente: {a.reemplaza}")

    nums = [int(re.search(r"\d+", e["id"]).group()) for e in entradas]
    vid = f"VER-{(max(nums) + 1 if nums else 1):04d}"
    entrada = {
        "id": vid,
        "fecha": datetime.now(ZoneInfo("America/Bogota")).isoformat(timespec="seconds"),
        "cambio": a.cambio,
        "veredicto": a.veredicto,
        "archivos": a.archivos,
        "hallazgos": hallazgos,
        "comprobaciones": a.comprobaciones,
        "rama": git("rev-parse", "--abbrev-ref", "HEAD"),
        "commit": git("rev-parse", "HEAD"),
        "reemplaza": a.reemplaza,
    }
    (carpeta / f"{vid}.json").write_text(json.dumps(entrada, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    entradas.append(entrada)
    regenerar(r, entradas)
    print(f"{vid} registrada: {a.veredicto} ({len(hallazgos)} hallazgos). Ver VERIFICACIONES.md")


if __name__ == "__main__":
    main()
