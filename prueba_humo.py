"""Prueba de humo del despliegue. Uso: python prueba_humo.py --url https://... (PT12)."""
import argparse
import sys
import urllib.request


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    url = ap.parse_args().url.rstrip("/")
    try:
        with urllib.request.urlopen(url + "/_stcore/health", timeout=15) as r:
            ok = r.status == 200
    except Exception as e:  # noqa: BLE001
        print(f"FALLA: {e}")
        return 1
    print("OK: la aplicación responde" if ok else "FALLA: respuesta inesperada")
    print("Pendiente (PT12): comprobar datos y acta.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
