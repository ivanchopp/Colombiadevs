# AVANCES

> **Si eres un chat nuevo de Claude Code, empieza aquí.** Este archivo es la memoria del proyecto: qué se quiere hacer, qué ya se hizo, qué falta y qué sigue. Léelo completo antes de tocar nada y **actualízalo al terminar cada cambio** (ver «Cómo mantener este archivo»).

**Última actualización:** sáb 17 oct 2026, 13:20 (hora Bogotá)
**Entrega:** **dom 18 oct 2026, 8:00 a. m. (hora Bogotá).** Objetivo: enviar a las 7:00.
**Repositorio:** https://github.com/ivanchopp/Colombiadevs · rama `main` (incluye el PR #2, commit `77a8763`). El trabajo nuevo se hace en ramas `claude/*` y entra por PR.

---

## 1. En 30 segundos

- **Qué es:** un agente que revisa las facturas de una empresa y decide, para cada una, si **pagar, frenar o escalar a una persona**, siguiendo reglas que la empresa define. Explica cada decisión. **No mueve dinero real.**
- **De dónde viene:** el *Reto Blinka, «Agentes que pagan por la empresa»* (Hackathon 30X, HackRadar). Blinka es una fintech colombiana en EE. UU. con cuentas en USD y pagos a Latinoamérica.
- **Idea central:** la IA solo **lee y redacta**. Un programa normal, el **motor de reglas**, **decide**. Ante la duda, el resultado es **escalar, nunca pagar**.
- **Equipo:** 4 personas. Reparto sugerido: **A** motor y pruebas · **B** agentes con IA · **C** pantallas · **D** datos, evaluación y pitch.
- **Estado del código (en `main`):** funciona de punta a punta el **motor de reglas**, el **acta** (SQLite), el **agente de entrada** y los **dos paneles** (Streamlit). **143 pruebas pasan** y `python3 eval.py` da **20 de 20, con 0 pagos indebidos**. La skill `verificador` aprobó la rama (VER-0005).
- **Lo que NO está probado:**
  1. **La lectura con IA real.** El agente lee con **Gemini o Claude** (intercambiables, ver `README.md`), pero solo se probó con clientes falsos, nunca con una clave. Sin clave corre en **modo demo**.
  2. **El despliegue en Railway.** Está preparado (`Dockerfile`, `railway.toml`) y se probó el arranque en local, pero la imagen de Docker y Railway no se han probado ni desplegado.
- **No existen todavía:** el agente de reglas, el agente de conciliación y las páginas de reglas y resumen (capa 3), PostgreSQL con permisos, y el simulador de cambios de reglas.
- **Para verlo:** `pip install -r requirements.txt` y `streamlit run app/Panel_1_Proveedor.py`. **Control de las 18:00:** `python3 eval.py`.

## 2. Lo que no se negocia

1. **Cero pagos fuera de las reglas.** Aprobar un pago indebido **descalifica** el proyecto.
2. **La IA nunca decide un pago.** Lee, pregunta, resume y propone reglas. Decide el código.
3. **Fallo seguro:** dato faltante, error o duda ⇒ `ESCALAR`.
4. **Cada decisión se puede explicar** leyendo su registro, sin abrir el código.
5. **Sin datos reales** de clientes ni empresas. Todo es ficticio y los valores de ejemplo se marcan como «supuesto».
6. **No se ejecutan pagos reales ni se mueve dinero.** «Pagar» es un pago de práctica que queda en el acta.
7. **Fuera del reto:** abrir cuentas, verificar identidades, decisiones de cumplimiento o de fraude, y el diseño de la app de Blinka.

**Criterios de éxito del reto:** *autonomía* (cuánto del set decide bien sin ayuda), *seguridad* (cero pagos indebidos) y *explicabilidad*.
**Entregable:** un agente funcionando sobre un set de facturas, con una pantalla donde la empresa define sus reglas y ve qué se pagó, qué se frenó, qué quedó pendiente de aprobación y por qué.

## 3. Alcance por capas

| Capa | Qué incluye | Hasta cuándo | Estado |
|---|---|---|---|
| **Núcleo** | Lectura de facturas con segunda lectura, motor de reglas con dos niveles de aprobación (persona y senior), acta con cadena de huellas, CSV y tablero, cola de aprobación, Panel 1, un test por caso trampa, despliegue en Railway | Sáb 18:00 | **Hecho**, salvo la lectura con IA real y el despliegue real (ver sección 1) |
| **Capa 2** | Sugerencia de canal de pago con las rutas de Blinka (Bre-B, SPEI, Pix, SEPA, transferencias locales, rutas en USD, ACH y wire, SWIFT, USDC), solo recomendación | Sáb 18:00 a 21:00, si el control de las 18:00 pasa | **Hecho** |
| **Capa 3** | Calendario de facturas esperadas, agente de reglas en lenguaje natural (con vigencias y detección de afloja/restringe), simular cambios, chat con el proveedor, agente de conciliación | Solo si sobra tiempo | Calendario y chat con el proveedor: **hechos**. Agente de reglas, vigencias con conflictos (T12), simular (T11) y conciliación: **no** |
| **A futuro** | Sello público del registro (raíz Merkle por lote anclada en testnet); billetera on-chain (Opción 5 de la guía), solo como visión en el pitch | No se construye | — |

**Orden para recortar** si algo se atrasa: agente de conciliación → chat con el proveedor → calendario → agente de reglas (dejar edición por formulario o YAML) → enrutador de canal. La Opción 1 sola ya cumple el entregable y los tres criterios.

## 4. Cómo funciona (resumen)

**Actores:**
- **Agente de entrada (IA):** recibe la factura, la lee (Gemini o Claude), pregunta al proveedor lo dudoso (máx. 2 turnos) y entrega una **ficha** estándar con el dato original y el aclarado. Una **segunda lectura** simple (patrones de texto) verifica a la IA, y otra detección sin IA busca órdenes escondidas. Spec en `specs/extraccion-y-agente-de-entrada/`.
- **Motor de reglas (código, sin IA):** compara la ficha con los registros de la empresa, el calendario y las reglas vigentes. Decide `PAGAR`, `FRENAR` o `ESCALAR`, el nivel de aprobación, y sugiere un canal de pago. Spec en `specs/motor-de-reglas/`.
- **Agente de reglas (IA) — no construido:** convertiría una instrucción en lenguaje normal en un cambio de reglas, con vista previa y confirmación.
- **Agente de conciliación (IA) — no construido:** leería el acta (solo lectura), resumiría el periodo y avisaría de rarezas. No calcularía cifras.
- **Acta:** registro de solo añadir; cada fila lleva la huella de la anterior. De ahí salen el CSV y el tablero.
- **Persona de finanzas / senior de finanzas:** aprueban lo escalado según su nivel. Solo el senior aprueba lo de mayor riesgo y (cuando exista el agente de reglas) firma los cambios que *aflojan* una regla.
- **Evaluadores de la demo:** hacen de proveedor en el Panel 1 y revisan en el Panel 2.

**Decisiones del motor** (parámetros de demostración en COP, todos «supuesto»):
- **Pagar:** todo OK, sin avisos y monto del periodo para ese beneficiario ≤ **3 M** (pago automático).
- **Frenar:** factura repetida, monto que supera lo acordado en más de **10 %**, sin presupuesto, o supera el techo duro (**50 M**).
- **Escalar:** cualquier duda. Nivel **persona** hasta **10 M**; **senior** por encima de 10 M o si hay riesgo (beneficiario nuevo, cuenta distinta, límite por periodo de **15 M** por beneficiario). Entre 5 % y 10 % sobre lo acordado: persona.
- **Presupuesto del periodo:** **100 M** COP. Moneda base: COP. Tolerancia normal: 5 %.

**Demo con dos paneles** que comparten una *sala* (un código por visitante en el enlace):
- **Panel 1, proveedor (abierto):** chat con el agente de entrada, subir PDF/foto/correo/TXT, botones de facturas de ejemplo (normal, repetida, beneficiario nuevo, con orden escondida) y estado de la factura. **Nunca muestra reglas ni límites.**
- **Panel 2, finanzas (con rol):** tablero con detalle de cada factura, cola de aprobación, calendario y acta. *(El chat de reglas y el resumen de conciliación no están construidos.)*

**Tecnología real:** Python 3.12 (`.python-version`, `Dockerfile`), **Gemini (`google-genai`) o Claude (`anthropic`)** para leer facturas, Pydantic, Streamlit (varias páginas), **SQLite** (en un volumen de Railway; PostgreSQL pendiente), pandas para el CSV, pytest y Hypothesis, imagen de Docker desplegada en **Railway**. Sin frameworks de agentes pesados.

## 5. Mapa del repositorio

| Ruta | Qué es |
|---|---|
| `AVANCES.md` | Este archivo |
| `CLAUDE.md` | Indicaciones cortas para Claude Code |
| `README.md` | Cómo correr, probar y desplegar; variables de entorno; Gemini o Claude |
| `docs/Ruta-de-una-factura.pdf` | **Diseño general:** actores, flujo, maquetas, herramientas, despliegue, a futuro. Se genera de una página en línea privada del equipo |
| `docs/Guia-6-alternativas-actualizada.pdf` | Guía de las 6 alternativas de @Marcelo Linero, ajustada a la entrega de las 8:00, con plan por horas |
| `specs/README.md` | Índice y reglas de las especificaciones |
| `specs/motor-de-reglas/` | 53 criterios EARS (R1 a R11), `design.md` (con «Ajustes al construir»), tareas T1 a T15 |
| `specs/acta-y-csv/` | 51 criterios (AC1 a AC9), diseño, tareas AT1 a AT10 |
| `specs/paneles-y-despliegue/` | Criterios PP1 a PP7 y PD1 (despliegue), diseño, tareas PT1 a PT11 |
| `specs/extraccion-y-agente-de-entrada/` | Criterios EA1 a EA9 y EA2b (proveedor intercambiable), diseño, tareas ET1 a ET8 |
| `.claude/skills/verificador/` | Skill que revisa cada cambio, lo aprueba o rechaza y lo registra. **Úsala antes de commitear.** |
| `VERIFICACIONES.md`, `.verificaciones/` | Historial de verificaciones (no se edita a mano) |
| `engine/` | Motor de reglas (sin IA): `modelos`, `evaluar`, `revisiones/` (entrada, frenar, beneficiario, montos, calendario), `niveles`, `canales`, `guardarrail`, `contexto` (desde el acta), `reglas_io` |
| `acta/` | Acta en SQLite: huellas, escribir, verificar, estado, CSV, tablero, salas. `esquema_postgres.sql` viene de otra sesión y **no se usa** todavía |
| `agents/` | Agente de entrada: `archivo`, `lectura_ia` (Gemini o Claude), `segunda_lectura` y `seguridad` (sin IA), `aclaraciones`, `estado`, `flujo`, `ejemplos`, `probar` |
| `app/` | Streamlit. `Panel_1_Proveedor.py`, `pages/` con el Panel 2 (Tablero, Cola de aprobación, Calendario, Acta), `comun.py`, `apoyo.py` |
| `data/` | `reglas.yaml`, `techos.yaml`, `registros.yaml`, `tasas.yaml`, `canales.yaml`, `calendario.csv` y `casos.yaml` (20 facturas de prueba), todo «supuesto»; `demo_semilla.py`; `facturas_ejemplo/` |
| `eval.py` | Mide autonomía, seguridad (pagos indebidos = 0) y explicabilidad con los 20 casos |
| `tests/`, `pytest.ini` | 143 pruebas (`python3 -m pytest -q`), incluida la de propiedades con Hypothesis |
| `Dockerfile`, `railway.toml`, `requirements-prod.txt`, `requirements.txt`, `.env.example`, `.streamlit/config.toml` | Despliegue y dependencias. La imagen corre como root a propósito (volúmenes de Railway) |

## 6. Registro de cambios

Lo más reciente va arriba.

| Cuándo | Commit | Qué se hizo |
|---|---|---|
| 17 oct | *(este commit)* | **P25 cerrado: R2.5 implementado.** Spec primero: `design.md` del motor alineado con el código (ficha con `origen_campos` y `segunda_lectura = no_disponible`; criterio R2.5 explicado campo por campo) y EA3.3 y EA6.4 ajustados. Código: R2.5 (un dato obligatorio que viene solo de una aclaración da `AVISO`, salvo que coincida con el acuerdo o el calendario; número y vencimiento siempre avisan), R2.2 con segunda lectura no disponible (imágenes y textos sin campos comparables) y el agente marca `origen_campos`. 11 pruebas nuevas, 4 violaciones nuevas en Hypothesis y 4 mutaciones del motor detectadas. 143 pruebas, `eval.py` 20/20. Diferencias deliberadas con el diseño de la otra sesión: `orden_en_texto` (agrega un `AVISO`) en lugar de `alerta_inyeccion`, y sin `campos_diferentes` ni `aclaraciones` en la ficha. |
| 17 oct | `be99999` | **Actualización de este archivo** tras fusionar el PR #2: se quitaron filas y pendientes duplicados, se corrigió el estado real, se agregó la deriva entre la spec del motor y el código (P25) y las decisiones abiertas que quedaron sin spec. |
| 17 oct | `77a8763` | **PR #2 fusionado en `main`:** motor de reglas, acta, agente de entrada, paneles y despliegue. |
| 17 oct | `e6a1e72` | **Fusión de `main` en la rama.** Otra sesión había subido a `main` un esqueleto paralelo (`agents/entrada/`, `app/componentes/`, 45 pruebas) y specs propias de paneles y extracción: 37 archivos en conflicto. Por decisión del dueño **ganó esta rama** (más completa). Se conservó de `main`: skill `verificador`, `.verificaciones/`, `VERIFICACIONES.md`, `pytest.ini`, `.python-version`, `acta/esquema_postgres.sql` y los arreglos de D2. El esqueleto paralelo salió del árbol y sigue en el historial (`cda2588`). Verificado: VER-0005. |
| 17 oct | `175774a` | **Proveedor de IA intercambiable (Gemini ahora, Claude después).** `PROVEEDOR_IA`, `GEMINI_API_KEY`/`GOOGLE_API_KEY`, `MODELO_GEMINI`; sin preferencia se usa Claude si hay clave, si no Gemini; si el elegido no tiene clave, modo demo. `python3 -m agents.probar` verifica la clave. 143 pruebas. |
| 17 oct | `dbc3d74` | **Despliegue preparado.** `Dockerfile`, `railway.toml`, `requirements-prod.txt`, `.env.example`, `README.md`; acta en el volumen de Railway con modo WAL; `FECHA_DEMO`. Se corrigió un error de arranque (`No module named 'agents'`). Probado en local: arranque, salud, persistencia, 6 visitantes a la vez, salas separadas. |
| 17 oct | `2e00975` | **Agente de entrada.** Valida el archivo por contenido real y tamaño; lectura con IA con esquema cerrado; segunda lectura sin IA; detección de órdenes escondidas; máx. 2 turnos; lo aclarado nunca reemplaza el original; arma la ficha y llama a `registrar_decision`. Modo demo sin clave. Panel 1 activo. |
| 17 oct | `a81775b` | **Canales de Blinka.** `canales.yaml` con las rutas reales (SPEI, Pix / TED, SEPA, Bre-B, CBU/CVU, transferencias locales, rutas en USD, ACH y wire, SWIFT, USDC). **PSE sale de los pagos:** solo recibe depósitos. Tasas supuestas para EUR, ARS, CLP, PEN, BOB, CRC y ZAR. |
| 17 oct | `02614d4` | **Motor de reglas.** T1 a T10 y T13 a T15 (faltan T11 simular y T12 vigencias con conflictos). Revisiones R2 a R6, niveles, canal sugerido, guardarraíl, reglas desde YAML con techo duro aparte, contexto armado desde el acta. 20 casos: **20/20, 0 pagos indebidos**. Los paneles pasan a usar decisiones reales del motor. |
| 17 oct | `1237c51` | **Primeros tableros.** Panel 1 y Panel 2 (tablero, cola de aprobación, calendario, acta, detalle), núcleo del acta en SQLite (AC1 a AC7). |
| 17 oct | `cda2588` | *(otra sesión)* Esqueleto paralelo del código: `engine`, `acta`, `agents/entrada`, `app`, 45 pruebas. **No está en el árbol actual** (ver `e6a1e72`). |
| 17 oct | `dc04e18` | *(otra sesión)* Specs de `paneles-y-despliegue` con criterios PD1 a PD12 y tareas PT1 a PT14. **Sustituidas** por las de esta rama (P23). |
| 17 oct | `24f1039` | *(otra sesión)* Interfaz pública del agente de entrada y documentación del verificador (VER-0003). |
| 17 oct | `7392522` | PR #1 de otra sesión: skill **`verificador`** (`3d9b7b3`), `monto_para_nivel` alineado con R5.2 (`0aecd8a`) y aclaración de D2 (`0b5e422`). VER-0001 y VER-0002. |
| 17 oct | `8bb35bb` | *(otra sesión)* Specs de `extraccion-y-agente-de-entrada` (EX1 a EX9, ET1 a ET11). Ajustó la spec del motor: R2.2, **nuevo R2.5** y campos nuevos de la ficha (ver P25). **Sustituidas** por las de esta rama (P23). |
| 17 oct | `8d91175` | Specs de `acta-y-csv`: 9 bloques de requisitos (AC1 a AC9), diseño y 10 tareas (AT1 a AT10). |
| 17 oct | `1d0a7d1` | Se crearon `AVANCES.md` y `CLAUDE.md`, para que cualquier chat nuevo de Claude Code conozca el proyecto. |
| 17 oct | `4ad15b4` | Se corrigieron las maquetas de «Ruta de una factura»: umbral de pago automático (3 M), motivo de la F-1045 y nivel de la F-1047 (persona, no senior). Presupuesto del periodo en **100 M**. PDF actualizado. |
| 17 oct | `77c9522` | Specs del motor de reglas: 11 bloques de requisitos, diseño y 15 tareas. Índice en `specs/README.md`. |
| 17 oct | *(análisis)* | Se estudió la documentación de feature specs de Kiro. Se adoptó el **método** (requisitos EARS, diseño y tareas) en `specs/`, sin instalar Kiro. |
| 17 oct | `d9dff20` | Guía de las 6 alternativas actualizada: entrega a las 8:00, plan por horas, Opción 6 reducida al enrutador de canal y sello público a futuro. |
| 17 oct | `2941e8c` | PDF de «Ruta de una factura» con la **sugerencia de canal de pago** (paso 8, maqueta, tabla de canales) y la sección «A futuro». |
| 17 oct | *(decisión)* | Se compararon la guía de @Marcelo Linero y nuestro diseño. Se **confirmó la entrega: dom 18 oct 8:00 a. m.** (antes se creía 12:00 y se había dicho 20:00). |
| 16–17 oct | *(sin commits)* | Diseño construido en conversación: agente de reglas, agente de entrada con chat al proveedor, calendario, agente de conciliación, CSV y tablero, niveles persona/senior, dos paneles con sala, 8 maquetas, despliegue solo en Railway. «Jurado» pasó a llamarse **«motor de reglas»**. |
| 16 oct | `7f9c408` | Primer PDF de «Ruta de una factura» en `docs/`. |
| 16 oct | *(inicio)* | Repositorio creado por el equipo como **`Colombiadevs`** (se había pedido «Colombia Devs»; GitHub no admite espacios). |

## 7. Cambios pendientes

Cosas ya hechas que hay que **revisar, confirmar o corregir**. Los números no se reutilizan: los que faltan ya se resolvieron o se descartaron.

**Lo más importante antes de la entrega**

| # | Pendiente | Quién / cómo |
|---|---|---|
| P20 | **Falta hacer el despliegue en Railway.** Ya se puede desplegar desde `main`. Pasos en `README.md`: conectar el repositorio, agregar un volumen en `/data`, poner `GEMINI_API_KEY` (o `ANTHROPIC_API_KEY`) y `FECHA_DEMO=2026-10-17`, generar el dominio, una sola réplica | Quien tenga Railway |
| P17 | **La lectura con IA no se probó con ninguna API real.** Claude: `messages.create` con `output_config.format`. Gemini: `generate_content` con `response_json_schema`. Los SDK aceptan la configuración, pero falta correr `python3 -m agents.probar` con una clave. **Los nombres de modelo por defecto no están verificados** (`gemini-2.5-flash`, `claude-sonnet-5-5`; se cambian con `MODELO_GEMINI` y `MODELO_ENTRADA`) | Quien tenga la clave (ET7) |
| P23 | **Specs de `main` sustituidas.** Las de `paneles-y-despliegue` (PD1 a PD12, PT1 a PT14) y `extraccion-y-agente-de-entrada` (EX1 a EX9, ET1 a ET11) de otra sesión se reemplazaron por las de esta rama, que describen el código existente. Siguen en el historial (`dc04e18`, `8bb35bb`). **El equipo debe confirmar cuáles valen**; la numeración y la interfaz pública del agente de entrada difieren | El equipo |
| P15 | **Calibración propia del motor** (D1 a D5 siguen abiertas): zona gris 5 % a 10 %, gasto cuenta solo lo pagado o aprobado, periodo = mes en Bogotá, y los ajustes de «Ajustes al construir». Las 20 facturas de `casos.yaml` se escribieron junto con el motor: **faltan casos trampa de otra mano** para que `eval.py` mida de verdad. R2.5 y R2.2 con segunda lectura no disponible tienen pruebas pero **no un caso en `casos.yaml`** (T3 pide uno por criterio) | D y el equipo |
| P18 | Las facturas de ejemplo dependen de la **fecha de hoy** (el calendario es de octubre de 2026, ventana de ±5 días): la «normal» solo se paga sola entre el 9 y el 19 de octubre. `FECHA_DEMO` lo evita | Poner `FECHA_DEMO` en Railway |

**Decisiones abiertas de las specs** (cada una tiene propuesta por defecto)

| # | Pendiente | Quién / cómo |
|---|---|---|
| P1 | **D1 a D5** de `specs/motor-de-reglas/requirements.md` (zona gris de 5 % a 10 %, qué cuenta en el gasto, periodo, preparador, valores por defecto) | El equipo |
| P9 | **DA1 a DA5** de `specs/acta-y-csv/requirements.md` (una fila por evento, cadena por sala, separador del CSV, reinicio de sala, sello público) | El equipo |
| P10 | **DE1 a DE4** de `specs/extraccion-y-agente-de-entrada/requirements.md` (el chat no devuelve `coincide`, no preguntar por la cuenta, modelo de lectura, datos enviados a Gemini) | El equipo |
| P11 | **DP1 y DP2** de `specs/paneles-y-despliegue/requirements.md` (una app o dos, qué ve la cola del senior). DP3 ya se resolvió | El equipo |

**Límites conocidos y deuda técnica**

| # | Pendiente | Quién / cómo |
|---|---|---|
| P2 | Se interpretó «aumenta el presupuesto 100M» como **fijarlo en 100 M**, no sumar 100 M (125 M) | Confirmar con el usuario |
| P3 | **Datos de Blinka:** canales y monedas salen del sitio oficial (captura del 17 oct). Siguen sin verificar los **costos, tiempos y límites** de cada ruta (están como «sin dato» o «supuesto»), y las redes de USDC no se usan | Verificar con Blinka si se quiere mostrar costos |
| P4 | Nombres de modelos sin verificar (ver P17). Las funciones de Streamlit (`st.query_params`, `st.fragment` con `run_every`, `st.segmented_control`) **sí se probaron** con Streamlit 1.66 | Quien monte el entorno |
| P5 | «Ruta de una factura» **no tiene** una sección «Plan hasta la entrega». Solo está en la guía | Opcional |
| P6 | **El PDF se genera a mano** desde la página en línea (Chromium, A3 horizontal). Si la página cambia, hay que regenerar y subir el PDF | Quien edite el diseño |
| P7 | Si se construye el sello público: confirmar con los organizadores que una **testnet no cuenta como mover dinero** | Solo si se retoma |
| P8 | Las fichas de la guía describen la **Opción 6 completa** a propósito. El alcance real es solo el enrutador | Solo saberlo |
| P12 | El menú lateral de Streamlit muestra «Cola de aprobacion» sin tilde (sale del nombre del archivo). Cosmético | Opcional: `st.navigation` |
| P13 | El acta usa **SQLite**. Falta PostgreSQL con roles y permisos (AC1.2); `acta/esquema_postgres.sql` existe pero no se usa ni se probó. No hay purga de salas (AC7.4) | Opcional, tras el despliegue |
| P14 | Falta un chequeo atómico entre validar y escribir una aprobación (hoy la clave de idempotencia evita la doble respuesta). Al pasar a PostgreSQL, validar dentro de la transacción | A |
| P19 | El agente no pregunta por la cuenta bancaria (DE2): solo se compara con los registros. Las imágenes siempre se escalan por no tener segunda lectura (EA3.3) | El equipo decide si basta |
| P21 | Con una sola réplica y SQLite no hay alta disponibilidad: un reinicio corta la demo unos segundos. Las salas viejas no se purgan | Aceptado para la entrega |
| P22 | Gemini en plan gratuito puede usar lo enviado para mejorar el producto: **solo facturas ficticias**. Un filtro de seguridad de Gemini puede bloquear una lectura (se trata como falla y se escala) | Saberlo |
| P24 | Los commits anteriores a la fusión no pasaron por el `verificador` (la regla llegó a `main` después); se verificó la rama completa de una vez (VER-0005) | Saberlo |

## 8. Próximas tareas

En orden. El detalle de cada tarea está en `tasks.md` de cada spec.

1. **Desplegar en Railway desde `main`** (P20) y abrirlo desde otro computador.
2. **Poner la clave de Gemini y correr `python3 -m agents.probar`** (P17). Si algo difiere, ajustar el modelo o la lectura.
3. **El equipo confirma las specs** que valen (P23) y resuelve las decisiones abiertas (P1, P9, P10, P11).
4. **Que otra persona escriba casos trampa nuevos** (P15) y los pase por `eval.py`.
5. **Control de las 18:00:** correr `eval.py`. El enrutador de canal ya está hecho; con tiempo, la capa 3 (agente de reglas, T11 simular, T12 vigencias, conciliación, páginas de reglas y resumen). Si los casos trampa no pasan, esas horas se usan para corregir el motor.

**Plan por horas** (hora de Bogotá):

| Bloque | Horario |
|---|---|
| Reglas y facturas ficticias | sáb 07:30 a 10:00 |
| Despliegue de prueba en Railway | sáb 08:30 a 10:00 |
| Extracción, motor y tests | sáb 10:00 a 14:00 |
| Pantalla y registro | sáb 15:00 a 18:00 |
| **Control: ¿pasan las trampas?** | **sáb 18:00** |
| Enrutador de canal de pago | sáb 18:00 a 21:00 |
| Pruebas y guion de demo | sáb 21:00 a 00:00 |
| Descanso | 00:00 a 05:00 |
| README, video y envío | dom 05:00 a 07:00 |
| Colchón. **Entrega a las 8:00** | dom 07:00 a 08:00 |

## 9. Convenciones y vocabulario

- **Idioma:** español, claro y sin jerga innecesaria.
- **Nombres:** *motor de reglas* (nunca «jurado», que se confundía con los jurados del hackathon); *evaluadores* son quienes prueban la demo; *ficha*, *acta*, *sala*, *agente de entrada*, *agente de reglas*, *agente de conciliación*.
- **Salidas:** `PAGAR`, `FRENAR`, `ESCALAR`. **Niveles:** `NINGUNO`, `PERSONA`, `SENIOR`. **Revisiones:** `OK`, `FALLA`, `AVISO`.
- **Specs:** requisitos en notación EARS («CUANDO … EL SISTEMA DEBERÁ …»), cada criterio con número y al menos una prueba.
- **Verificación:** antes de commitear o subir un cambio, pasarlo por la skill `verificador`. Deja un registro en `VERIFICACIONES.md`.
- **Commits:** en español, un resumen corto y un párrafo que explique el porqué. Trailer `Co-Authored-By: Claude <noreply@anthropic.com>`, sin versión del modelo.
- **Dinero:** `Decimal`, nunca `float`. Todo valor de ejemplo se marca como «supuesto».
- **Un cambio de plan se escribe primero en la spec** y después en el código.

## 10. Cómo mantener este archivo

Al terminar cualquier cambio:
1. Cambia **«Última actualización»** (fecha y hora de Bogotá).
2. Agrega una fila **arriba** en el registro de cambios (sección 6), con el commit si lo hay.
3. Mueve a la sección 7 lo que quedó por revisar y borra lo que ya se resolvió.
4. Ajusta la sección 8: tacha lo hecho y deja lo siguiente en orden.
5. Si cambió el alcance, la arquitectura o un parámetro, actualiza las secciones 2 a 4.
6. Mantén el archivo corto y legible: si una sección crece demasiado, resume y enlaza al documento.
