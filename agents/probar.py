"""Prueba rápida del proveedor de IA activo: lee las 4 facturas de ejemplo y compara con lo esperado.

Uso:  python3 -m agents.probar        (necesita GEMINI_API_KEY o ANTHROPIC_API_KEY)
Gasta unas pocas llamadas reales a la API."""
import sys

from . import archivo, ejemplos, lectura_ia, segunda_lectura


def main() -> int:
    proveedor = lectura_ia.proveedor_activo()
    if proveedor is None:
        print("No hay proveedor de IA: define GEMINI_API_KEY o ANTHROPIC_API_KEY (ver .env.example).")
        return 2
    print(f"Proveedor: {lectura_ia.descripcion_proveedor()}\n")
    fallas = 0
    for clave in ejemplos.EJEMPLOS:
        nombre, datos = ejemplos.leer_ejemplo(clave)
        tipo = archivo.validar(nombre, datos)
        texto = archivo.extraer_texto(tipo, datos)
        esperado = lectura_ia._limpiar(ejemplos.LECTURAS_GUARDADAS[clave])
        try:
            leido = lectura_ia.leer_con_ia(tipo, datos, texto)
        except lectura_ia.LecturaFallida as e:
            print(f"FALLA {clave}: {e}")
            fallas += 1
            continue
        difieren = [c for c in ("beneficiario", "numero", "monto", "moneda", "vence")
                    if str(leido[c]) != str(esperado[c])]
        segunda, _ = segunda_lectura.comparar(leido, texto)
        estado = "OK   " if not difieren and segunda == "coincide" else "DIFIERE"
        fallas += estado != "OK   "
        print(f"{estado} {clave}: segunda lectura {segunda}" + (f", difieren: {difieren}" if difieren else ""))
        if difieren:
            print("       leído:", {c: str(leido[c]) for c in difieren},
                  "esperado:", {c: str(esperado[c]) for c in difieren})
    print(f"\n{'Todo bien.' if not fallas else f'{fallas} de {len(ejemplos.EJEMPLOS)} con problemas.'}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
