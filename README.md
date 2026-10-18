# Colombiadevs · Agente que paga por la empresa

Reto Blinka, «Agentes que pagan por la empresa» (Hackathon 30X). Es un agente para las **empresas clientes de Blinka**: revisa las facturas de sus proveedores y decide si **pagar, frenar o escalar** cada una, siguiendo las reglas de la empresa y explicando cada decisión. Al final entrega a Blinka un **archivo con las facturas aprobadas** (automática o manualmente) para que Blinka haga los pagos desde la cuenta del cliente. Nosotros somos la capa de control antes del pago (aclarado por Blinka el 17 oct; ver `AVANCES.md`, secciones 1b y 8b).

> **No mueve dinero real y solo usa datos ficticios.** «Pagar» es una aprobación de práctica que queda en el acta. El archivo de salida con los pagos aprobados (`pagos_aprobados.csv`, en la página Acta del Panel 2) ya se genera; sus columnas son un supuesto hasta confirmar el formato de Blinka (`specs/archivo-de-salida/`).

## Idea central

La IA **solo lee y pregunta**. Quien **decide** es el **motor de reglas**, código normal sin IA. Ante la duda, el resultado es `ESCALAR`, nunca `PAGAR`. Todo lo que viene de fuera (la factura y el chat) es un dato no confiable: se lee, nunca se obedece.

| Pieza | Qué hace | Dónde |
|---|---|---|
| Agente de entrada (IA) | Lee la factura, la verifica con una segunda lectura sin IA, pregunta lo dudoso (máx. 2 turnos) y arma la ficha | `agents/` |
| Motor de reglas (sin IA) | Decide `PAGAR`, `FRENAR` o `ESCALAR`, el nivel de aprobación y sugiere un canal | `engine/` |
| Acta | Registro de solo añadir con cadena de huellas; de ahí salen el CSV y el tablero | `acta/` |
| Panel 1 (proveedor) | Sube facturas, chatea con el agente, ve solo el estado de su factura | `app/Envía_facturas.py` |
| Panel 2 (finanzas) | Tablero, cola de aprobación, calendario, acta, órdenes de compra, reglas (ver, cambiar y firmar) y descarga de CSV | `app/pages/` |

Más contexto: `AVANCES.md` (estado y pendientes), `specs/` (requisitos de cada parte) y `docs/`.

## Probarlo en local

```bash
pip install -r requirements.txt
streamlit run app/Envía_facturas.py      # abre el Panel 1; el Panel 2 está en el menú lateral
python3 -m pytest -q                         # pruebas
python3 eval.py                              # autonomía, seguridad y explicabilidad con 29 facturas
```

### IA para leer facturas: Gemini o Claude

La lectura de facturas funciona con **Gemini** o con **Claude**, con el mismo esquema de salida, las mismas defensas y el mismo motor de reglas. Cambiar de uno a otro es solo cambiar variables de entorno:

| Variable | Para qué |
|---|---|
| `GEMINI_API_KEY` (o `GOOGLE_API_KEY`) | Usar Gemini. Modelo por defecto `gemini-3.8-flash` (cámbialo con `MODELO_GEMINI`; los nombres de modelo de Google cambian, y `gemini-2.5-flash` dejó de estar disponible el 17 oct) |
| `ANTHROPIC_API_KEY` | Usar Claude. Modelo por defecto `claude-sonnet-5-5` (cámbialo con `MODELO_ENTRADA`) |
| `PROVEEDOR_IA` | `gemini` o `claude`. Si lo dejas vacío: Claude si hay clave de Claude; si no, Gemini |

**Si la IA «está activa» pero no lee:** abre la app con `?diagnostico=1`. Ahí se ve la **última falla de lectura** y el botón **«Probar la conexión con la IA ahora»**, que muestra el error y, para Gemini, los modelos disponibles; si el modelo ya no existe, cambia `MODELO_GEMINI`. Una falla de la IA no se avisa en pantalla: la factura se lee con patrones y pasa a revisión de una persona.

**Para pasar de Gemini a Claude:** agrega `ANTHROPIC_API_KEY` y borra `GEMINI_API_KEY` (o pon `PROVEEDOR_IA=claude`). No hay que tocar el código.

Verifica que la clave funciona (hace unas pocas llamadas reales):

```bash
GEMINI_API_KEY=... python3 -m agents.probar
```

Sin ninguna clave la app corre en **modo demo**: los archivos se leen solo con patrones de texto, así que **siempre pasan a revisión de una persona** (nunca se paga). Los nombres de los modelos pueden cambiar: si la API dice que no existe, ajusta `MODELO_GEMINI` o `MODELO_ENTRADA`.

### Archivos de muestra

El Panel 1 no tiene botones de ejemplo: el sistema lee el archivo que subes y el motor de reglas decide. Para probar los cuatro casos, abre «Archivos de muestra (ficticios)» en el Panel 1, descarga y vuelve a subir (con la IA activa, en una sala nueva):

| Archivo | Qué debe pasar |
|---|---|
| Alimentos del Valle S.A.S. · IS-2210 | Normal: se aprueba para pagar |
| Papelería Corporativa Anáhuac S.A. de C.V. · TA-0931 | Repetida: se frena (la sala nueva ya trae esa factura en el acta) |
| Estudio Nube · EN-0077 | Beneficiario nuevo: se escala al senior |
| Consultores Energéticos Magdalena S.A.S. · HA-5531 | Trae una orden escondida en el texto: se escala a una persona |

Las fechas dependen de `FECHA_DEMO` (ver AVANCES P18).

> Usa solo facturas **ficticias**. Los planes gratuitos de Gemini pueden usar lo que se envía para mejorar el producto.

## Desplegar en Railway

La app se despliega con el `Dockerfile` y `railway.toml` de este repositorio. Pasos:

1. En Railway: **New Project → Deploy from GitHub repo** → `ivanchopp/Colombiadevs` (elige la rama que quieras desplegar).
2. **Agrega un volumen** al servicio (Service → Volumes) montado en `/data`. Ahí se guarda el acta. Railway define solo `RAILWAY_VOLUME_MOUNT_PATH`. **Sin volumen, los datos se pierden en cada reinicio.**
3. **Variables** (Service → Variables). Los nombres están en `.env.example`:
   - `GEMINI_API_KEY` (ahora) o `ANTHROPIC_API_KEY` (después): para leer facturas con la IA real. Sin clave, modo demo. Ver «IA para leer facturas».
   - `FACTURAS_MAX` (opcional): facturas que cada sala puede subir, de 1 a 100 (por defecto 5). Cada una gasta una llamada de IA, así que súbelo con cuidado. No es un tope de gasto real: ese se pone en Google AI Studio o Google Cloud.
   - `FECHA_DEMO=2026-10-17`: recomendado. Fija «hoy» para que el calendario y las reglas no dependan del día en que se pruebe.
4. **Settings → Networking → Generate Domain** para tener el enlace público.
5. Déjalo en **una sola réplica** (el acta usa SQLite sobre el volumen).
6. Comprueba `https://<tu-dominio>/_stcore/health` (debe responder `ok`) y abre la app.

Qué se probó y qué no: el arranque, la comprobación de salud, la persistencia en el volumen, 6 visitantes a la vez y la separación entre salas se probaron localmente con solo las dependencias de producción. El equipo **desplegó la app en Railway el 17 oct** (commit `014409d`) y se probó desde fuera: salud `ok`, Gemini activo y `FECHA_DEMO` definida. Falta comprobar que el acta sobrevive a un reinicio y que el despliegue corre el último `main` (ver `AVANCES.md`, P32).

## Límites conocidos

- Los valores (montos, tasas, costos, límites) son de **demostración** y están marcados como «supuesto».
- El acta usa **SQLite**. La inmutabilidad la garantizan triggers y la cadena de huellas; falta PostgreSQL con permisos de base de datos (ver `AVANCES.md`, P13).
- También se acepta el **XML de la factura electrónica**, sin IA: UBL 2.1 (Colombia y Perú), CFDI de México (solo de tipo ingreso), SRI de Ecuador, CFE de Uruguay, NF-e de Brasil, DTE de Chile, Costa Rica y SIFEN de Paraguay. Se revisa en local solo el dígito del NIT colombiano y del RFC mexicano. Un XML de otro formato (por ejemplo de Argentina o Venezuela, que no tienen un XML común entre empresas) se lee como texto y siempre se escala. **No consulta a ninguna autoridad tributaria.**
- La lectura con **Gemini** se probó en Railway con los textos de ejemplo; falta probarla con un PDF o una foto propios (P17). **Claude** no se ha probado contra la API real.
- No hay inicio de sesión: el Panel 2 usa un selector de rol de demostración.
