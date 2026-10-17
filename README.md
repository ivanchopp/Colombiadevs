# Colombiadevs · Agente que paga por la empresa

Reto Blinka, «Agentes que pagan por la empresa» (Hackathon 30X). Un agente revisa las facturas de una empresa y decide si **pagar, frenar o escalar** cada una, siguiendo las reglas de la empresa y explicando cada decisión.

> **No mueve dinero real y solo usa datos ficticios.** «Pagar» es un pago de práctica que queda en el acta.

## Idea central

La IA **solo lee y pregunta**. Quien **decide** es el **motor de reglas**, código normal sin IA. Ante la duda, el resultado es `ESCALAR`, nunca `PAGAR`. Todo lo que viene de fuera (la factura y el chat) es un dato no confiable: se lee, nunca se obedece.

| Pieza | Qué hace | Dónde |
|---|---|---|
| Agente de entrada (IA) | Lee la factura, la verifica con una segunda lectura sin IA, pregunta lo dudoso (máx. 2 turnos) y arma la ficha | `agents/` |
| Motor de reglas (sin IA) | Decide `PAGAR`, `FRENAR` o `ESCALAR`, el nivel de aprobación y sugiere un canal | `engine/` |
| Acta | Registro de solo añadir con cadena de huellas; de ahí salen el CSV y el tablero | `acta/` |
| Panel 1 (proveedor) | Sube facturas, chatea con el agente, ve solo el estado de su factura | `app/Panel_1_Proveedor.py` |
| Panel 2 (finanzas) | Tablero, cola de aprobación, calendario, acta y descarga de CSV | `app/pages/` |

Más contexto: `AVANCES.md` (estado y pendientes), `specs/` (requisitos de cada parte) y `docs/`.

## Probarlo en local

```bash
pip install -r requirements.txt
streamlit run app/Panel_1_Proveedor.py      # abre el Panel 1; el Panel 2 está en el menú lateral
python3 -m pytest -q                         # pruebas
python3 eval.py                              # autonomía, seguridad y explicabilidad con 20 facturas
```

### IA para leer facturas: Gemini o Claude

La lectura de facturas funciona con **Gemini** o con **Claude**, con el mismo esquema de salida, las mismas defensas y el mismo motor de reglas. Cambiar de uno a otro es solo cambiar variables de entorno:

| Variable | Para qué |
|---|---|
| `GEMINI_API_KEY` (o `GOOGLE_API_KEY`) | Usar Gemini. Modelo por defecto `gemini-2.5-flash` (cámbialo con `MODELO_GEMINI`) |
| `ANTHROPIC_API_KEY` | Usar Claude. Modelo por defecto `claude-sonnet-5-5` (cámbialo con `MODELO_ENTRADA`) |
| `PROVEEDOR_IA` | `gemini` o `claude`. Si lo dejas vacío: Claude si hay clave de Claude; si no, Gemini |

**Para pasar de Gemini a Claude:** agrega `ANTHROPIC_API_KEY` y borra `GEMINI_API_KEY` (o pon `PROVEEDOR_IA=claude`). No hay que tocar el código.

Verifica que la clave funciona (hace unas pocas llamadas reales):

```bash
GEMINI_API_KEY=... python3 -m agents.probar
```

Sin ninguna clave la app corre en **modo demo**: las 4 facturas de ejemplo usan lecturas guardadas y los archivos propios se leen solo con patrones de texto, así que pasan a revisión de una persona. Los nombres de los modelos pueden cambiar: si la API dice que no existe, ajusta `MODELO_GEMINI` o `MODELO_ENTRADA`.

> Usa solo facturas **ficticias**. Los planes gratuitos de Gemini pueden usar lo que se envía para mejorar el producto.

## Desplegar en Railway

La app se despliega con el `Dockerfile` y `railway.toml` de este repositorio. Pasos:

1. En Railway: **New Project → Deploy from GitHub repo** → `ivanchopp/Colombiadevs` (elige la rama que quieras desplegar).
2. **Agrega un volumen** al servicio (Service → Volumes) montado en `/data`. Ahí se guarda el acta. Railway define solo `RAILWAY_VOLUME_MOUNT_PATH`. **Sin volumen, los datos se pierden en cada reinicio.**
3. **Variables** (Service → Variables). Los nombres están en `.env.example`:
   - `GEMINI_API_KEY` (ahora) o `ANTHROPIC_API_KEY` (después): para leer facturas con la IA real. Sin clave, modo demo. Ver «IA para leer facturas».
   - `FECHA_DEMO=2026-10-17`: recomendado. Fija «hoy» para que el calendario y las reglas no dependan del día en que se pruebe.
4. **Settings → Networking → Generate Domain** para tener el enlace público.
5. Déjalo en **una sola réplica** (el acta usa SQLite sobre el volumen).
6. Comprueba `https://<tu-dominio>/_stcore/health` (debe responder `ok`) y abre la app.

Qué se probó y qué no: el arranque, la comprobación de salud, la persistencia en el volumen, 6 visitantes a la vez y la separación entre salas se probaron localmente con solo las dependencias de producción. **La imagen de Docker y el despliegue real no se han probado** (no hay Docker ni acceso a Railway en el entorno de desarrollo).

## Límites conocidos

- Los valores (montos, tasas, costos, límites) son de **demostración** y están marcados como «supuesto».
- El acta usa **SQLite**. La inmutabilidad la garantizan triggers y la cadena de huellas; falta PostgreSQL con permisos de base de datos (ver `AVANCES.md`, P13).
- La lectura con IA real (Gemini y Claude) está sin probar contra las APIs reales hasta contar con una clave (P17). Se probó con clientes falsos y construyendo los clientes de los SDK sin red.
- No hay inicio de sesión: el Panel 2 usa un selector de rol de demostración.
