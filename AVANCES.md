# AVANCES

> **Si eres un chat nuevo de Claude Code, empieza aquí.** Este archivo es la memoria del proyecto: qué se quiere hacer, qué ya se hizo, qué falta y qué sigue. Léelo completo antes de tocar nada y **actualízalo al terminar cada cambio** (ver «Cómo mantener este archivo»).

**Última actualización:** sáb 17 oct 2026, 18:30 (hora Bogotá)
**Entrega:** **dom 18 oct 2026, 8:00 a. m. (hora Bogotá).** Objetivo: enviar a las 7:00.
**Repositorio:** https://github.com/ivanchopp/Colombiadevs (rama `main`, no hay otras)

---

## 1. En 30 segundos

- **Qué es:** un agente que revisa las facturas de una empresa y decide, para cada una, si **pagar, frenar o escalar a una persona**, siguiendo reglas que la empresa define. Explica cada decisión. **No mueve dinero real.**
- **De dónde viene:** el *Reto Blinka, «Agentes que pagan por la empresa»* (Hackathon 30X, HackRadar). Blinka es una fintech colombiana en EE. UU. con cuentas en USD y pagos a Latinoamérica.
- **Idea central:** la IA solo **lee y redacta**. Un programa normal, el **motor de reglas**, **decide**. Ante la duda, el resultado es **escalar, nunca pagar**.
- **Equipo:** 4 personas. Reparto sugerido: **A** motor y pruebas · **B** agentes con IA · **C** pantallas · **D** datos, evaluación y pitch.
- **Estado del código:** hay **el motor de reglas, el acta (SQLite), el agente de entrada y los dos paneles (Streamlit)**, con 132 pruebas y `eval.py` en 20 de 20. **El agente de entrada nunca se ha probado contra una API real** (falta clave): lee con **Gemini o Claude** (intercambiables, ver `README.md`) y sin clave corre en **modo demo**. El **despliegue en Railway está preparado pero no hecho** (ver `README.md`). Faltan el agente de reglas y el de conciliación (capa 3). Para verlo: `pip install -r requirements.txt` y `streamlit run app/Panel_1_Proveedor.py`. Control de las 18:00: `python3 eval.py`.

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

| Capa | Qué incluye | Hasta cuándo |
|---|---|---|
| **Núcleo** | Lectura de facturas con segunda lectura, motor de reglas con dos niveles de aprobación (persona y senior), acta con cadena de huellas, CSV y tablero, cola de aprobación, Panel 1 mínimo, un test por caso trampa, despliegue en Railway | Sáb 18:00 |
| **Capa 2** | Sugerencia de canal de pago (USDC, ACH/wire, Bre-B, PSE), solo recomendación | Sáb 18:00 a 21:00, si el control de las 18:00 pasa |
| **Capa 3** | Calendario de facturas esperadas, agente de reglas en lenguaje natural (con vigencias y detección de afloja/restringe), simular cambios, chat con el proveedor, agente de conciliación | Solo si sobra tiempo |
| **A futuro** | Sello público del registro (raíz Merkle por lote anclada en testnet); billetera on-chain (Opción 5 de la guía), solo como visión en el pitch | No se construye |

**Orden para recortar** si algo se atrasa: agente de conciliación → chat con el proveedor → calendario → agente de reglas (dejar edición por formulario o YAML) → enrutador de canal. La Opción 1 sola ya cumple el entregable y los tres criterios.

## 4. Cómo funciona (resumen)

**Actores:**
- **Agente de entrada (IA):** recibe la factura, la lee, pregunta al proveedor lo dudoso (máx. 2 turnos) y entrega una **ficha** estándar (JSON) con el dato original y el aclarado. Una **segunda lectura** simple (patrones de texto) verifica a la IA.
- **Motor de reglas (código, sin IA):** compara la ficha con los registros de la empresa, el calendario y las reglas vigentes. Decide `PAGAR`, `FRENAR` o `ESCALAR`, el nivel de aprobación, y sugiere un canal de pago. Spec en `specs/motor-de-reglas/`.
- **Agente de reglas (IA):** convierte una instrucción en lenguaje normal en un cambio de reglas, pregunta lo ambiguo, muestra vista previa y espera confirmación.
- **Agente de conciliación (IA):** lee el acta (solo lectura), resume el periodo y avisa de rarezas. No calcula cifras.
- **Acta:** registro de solo añadir; cada fila lleva la huella de la anterior. De ahí salen el CSV y el tablero.
- **Persona de finanzas / senior de finanzas:** aprueban lo escalado según su nivel. Solo el senior aprueba lo de mayor riesgo y firma los cambios que *aflojan* una regla.
- **Evaluadores de la demo:** hacen de proveedor en el Panel 1 y revisan en el Panel 2.

**Decisiones del motor** (parámetros de demostración en COP):
- **Pagar:** todo OK, sin avisos y monto del periodo para ese beneficiario ≤ **3 M** (pago automático).
- **Frenar:** factura repetida, monto que supera lo acordado en más de **10 %**, sin presupuesto, o supera el techo duro (**50 M**).
- **Escalar:** cualquier duda. Nivel **persona** hasta **10 M**; **senior** por encima de 10 M o si hay riesgo (beneficiario nuevo, cuenta distinta, límite por periodo de **15 M** por beneficiario). Entre 5 % y 10 % sobre lo acordado: persona.
- **Presupuesto del periodo:** **100 M** COP. Moneda base: COP. Tolerancia normal: 5 %.

**Demo con dos paneles** que comparten una *sala* (un código por visitante en el enlace):
- **Panel 1, proveedor (abierto):** chat con el agente de entrada, subir PDF/foto/correo, botones de facturas de ejemplo (normal, repetida, beneficiario nuevo, con orden escondida) y estado de la factura. **Nunca muestra reglas ni límites.**
- **Panel 2, finanzas (con rol):** tablero, cola de aprobación, calendario, acta, chat de reglas y resumen.

**Tecnología prevista:** Python 3.11+, API de Claude (SDK `anthropic`), Pydantic, Streamlit (varias páginas), PostgreSQL de Railway (SQLite en local), pandas para el CSV, pytest y Hypothesis, despliegue en **Railway**. Sin frameworks de agentes pesados.

## 5. Mapa del repositorio

| Ruta | Qué es |
|---|---|
| `AVANCES.md` | Este archivo |
| `CLAUDE.md` | Indicaciones cortas para Claude Code |
| `docs/Ruta-de-una-factura.pdf` | **Diseño general:** actores, flujo, maquetas, herramientas, despliegue, a futuro. Se genera de una página en línea privada del equipo |
| `docs/Guia-6-alternativas-actualizada.pdf` | Guía de las 6 alternativas de @Marcelo Linero, ajustada a la entrega de las 8:00, con plan por horas |
| `specs/README.md` | Índice y reglas de las especificaciones |
| `.claude/skills/verificador/` | Skill que revisa cada cambio, lo aprueba o rechaza y lo registra. **Úsala antes de commitear.** |
| `.claude/skills/sales-narrative/`, `storytelling/` | Skills de terceros adaptadas para armar el pitch de ventas y el guion de la demo (ver registro de cambios) |
| `VERIFICACIONES.md`, `.verificaciones/` | Historial de verificaciones (no se edita a mano) |
| `specs/motor-de-reglas/` | `requirements.md` (53 criterios EARS), `design.md`, `tasks.md` (T1 a T15) |
| `specs/paneles-y-despliegue/` | Los dos paneles de la demo, la sala, los roles, el refresco, el despliegue en Railway, las protecciones y la prueba de humo. `requirements.md` (criterios PD), `design.md`, `tasks.md` (PT1 a PT14) |
| `specs/extraccion-y-agente-de-entrada/` | Agente de entrada con IA: recepción, extracción, segunda lectura, preguntas al proveedor, defensa contra órdenes escondidas y modo demo. `requirements.md` (criterios EX), `design.md`, `tasks.md` (ET1 a ET11) |
| `specs/acta-y-csv/` | Acta de solo añadir con huellas, CSV, tablero, salas y agente de conciliación. `requirements.md` (criterios AC), `design.md`, `tasks.md` (AT1 a AT10) |
| `specs/paneles-y-despliegue/` | Requisitos (PP1 a PP7), diseño y tareas (PT1 a PT11) de los dos paneles |
| `app/` | Streamlit. `Panel_1_Proveedor.py` (portal abierto), `pages/` con el Panel 2 (Tablero, Cola de aprobación, Calendario, Acta), `comun.py` (sala, rol) y `apoyo.py` (funciones puras) |
| `acta/` | Núcleo mínimo del acta en SQLite: huellas, escribir, verificar, estado, CSV, tablero, salas |
| `engine/` | Motor de reglas (sin IA): `modelos`, `evaluar`, `revisiones/` (entrada, frenar, beneficiario, montos, calendario), `canales`, `guardarrail`, `contexto` (desde el acta), `reglas_io` |
| `data/*.yaml`, `calendario.csv`, `casos.yaml` | Reglas, techos, registros, tasas, canales (todo «supuesto»), calendario y las 20 facturas de prueba |
| `data/demo_semilla.py` | 6 facturas de ejemplo de las maquetas; cada una pasa por el motor |
| `agents/` | Agente de entrada: `archivo` (tipo real, 5 MB), `lectura_ia` (Claude, esquema cerrado, cliente inyectable), `segunda_lectura` y `seguridad` (sin IA), `aclaraciones` (máx. 2 turnos), `estado`, `flujo` (arma la ficha y llama al motor), `ejemplos` |
| `specs/extraccion-y-agente-de-entrada/` | Requisitos (EA1 a EA9), diseño y tareas (ET1 a ET7) |
| `data/facturas_ejemplo/` | Las 4 facturas de ejemplo como texto (normal, repetida, beneficiario nuevo, orden escondida) |
| `eval.py` | Mide autonomía, seguridad (pagos indebidos = 0) y explicabilidad con los 20 casos |
| `README.md`, `Dockerfile`, `railway.toml`, `.env.example`, `requirements-prod.txt` | Cómo correr y desplegar. La imagen corre como root a propósito (volúmenes de Railway) |
| `agents/probar.py` | `python3 -m agents.probar`: prueba la clave real leyendo las 4 facturas de ejemplo |
| `tests/` | 132 pruebas (`python3 -m pytest -q`), incluida la de propiedades con Hypothesis |
| *(aún no existe)* `agents/`, `init_db.py` | Estructura de código prevista |

## 6. Registro de cambios

Lo más reciente va arriba.

| Cuándo | Commit | Qué se hizo |
|---|---|---|
| 17 oct | *(este commit)* | **Skills de pitch.** Se instalaron `sales-narrative` (guia-matthieu/clawfu-skills, MIT, narrativa de 8 pasos de April Dunford) y `storytelling` (gtmagents/gtm-agents, arco SCAR) y se revisaron: son solo Markdown, sin scripts. Se adaptaron en `.claude/skills/` (español, reglas del proyecto, escenas con las 4 facturas de ejemplo). Se quitó de `sales-narrative` el texto ajeno a ventas (secciones de producción de audio). Las cifras del pitch deben salir de `eval.py` del día; sin clientes ni citas inventadas. |
| 17 oct | *(este commit)* | **Fusión con `main`.** Otra sesión había subido a `main` un esqueleto paralelo (`agents/entrada/`, `app/componentes/`, 45 pruebas) y specs propias de paneles y extracción: 37 archivos en conflicto. Por decisión del dueño **gana esta rama** (más completa: motor 20 de 20, 132 pruebas, agente con Gemini/Claude, paneles, despliegue). Se conserva de `main`: la skill `verificador`, `.verificaciones/`, `VERIFICACIONES.md`, `pytest.ini`, `.python-version`, `acta/esquema_postgres.sql` y los arreglos de D2. Se sacó del árbol el esqueleto paralelo (sigue en el historial de `main`, commit `cda2588`). Verificado con la skill `verificador`. |
| 17 oct | *(este commit)* | **Proveedor de IA intercambiable (Gemini ahora, Claude después).** Spec EA2b. `PROVEEDOR_IA`, `GEMINI_API_KEY`/`GOOGLE_API_KEY`, `MODELO_GEMINI`; sin preferencia se usa Claude si hay clave, si no Gemini; si el elegido no tiene clave, modo demo. Mismo esquema, mismas defensas y mismo motor. La pantalla muestra qué proveedor está activo. `python3 -m agents.probar` verifica la clave. Probado con clientes falsos de los dos proveedores y construyendo los clientes reales de los SDK sin red. 132 pruebas. |
| 17 oct | *(commit anterior)* | **Despliegue preparado.** `Dockerfile`, `railway.toml` (salud en `/_stcore/health`), `requirements-prod.txt`, `.env.example` y `README.md`. El acta va al volumen de Railway (`RAILWAY_VOLUME_MOUNT_PATH`) con modo WAL; `FECHA_DEMO` fija «hoy». Se encontró y corrigió un error de arranque (`No module named 'agents'` con el comando de Railway) probando con solo las dependencias de producción. Probado en local: arranque, salud, persistencia tras reiniciar, 6 visitantes a la vez y salas separadas. **No se probó la imagen de Docker ni Railway** (no hay Docker ni acceso). |
| 17 oct | *(commit anterior)* | **Agente de entrada.** Spec `extraccion-y-agente-de-entrada` y código. Valida el archivo por contenido real y tamaño; lee con Claude (un solo llamado, esquema cerrado, factura marcada como dato no confiable, sin reglas ni registros); segunda lectura con patrones de texto; detección de órdenes escondidas sin IA; máx. 2 turnos con preguntas de plantilla; lo aclarado nunca reemplaza el original; arma la ficha y llama a `registrar_decision`. Modo demo sin clave: lecturas guardadas para los 4 ejemplos y archivos propios siempre escalados. Panel 1 activo (subida, ejemplos, chat). Las 4 facturas de ejemplo dan normal → PAGAR, repetida → FRENAR, nuevo → SENIOR, orden escondida → ESCALAR. |
| 17 oct | *(commit anterior)* | **Canales de Blinka.** Con la captura del sitio de Blinka que aportó el equipo, `canales.yaml` pasa a las rutas reales (SPEI, Pix / TED, SEPA, Bre-B, CBU/CVU, transferencias locales, rutas locales en USD, ACH y wire, SWIFT, USDC). **PSE se quita de los pagos:** solo recibe depósitos. Se agregaron tasas supuestas para EUR, ARS, CLP, PEN, BOB, CRC y ZAR. El caso C15 usa ahora JPY como moneda sin tasa. 72 pruebas, 20 de 20. |
| 17 oct | *(commit anterior)* | **Motor de reglas.** T1 a T10, T13 a T15 (falta T11 simular y T12 vigencias con conflictos). Revisiones R2 a R6, niveles, sugerencia de canal, guardarraíl (`registrar_decision` revalida y rechaza pagos fuera de reglas; `validar_aprobacion` con rol, motivo, separación de funciones y techo duro), reglas cargadas de YAML con techo duro aparte, contexto armado desde el acta. 20 casos con decisión esperada: **20/20, 0 pagos indebidos**. Hypothesis sin pagos indebidos. Los paneles ya usan decisiones reales del motor, no la semilla escrita a mano. Ajustes de diseño en `specs/motor-de-reglas/design.md` («Ajustes al construir»). |
| 17 oct | *(commit anterior)* | **Primeros tableros.** Spec `paneles-y-despliegue` (PP1 a PP7). Código: Panel 1 (estado público, sin reglas ni motivos) y Panel 2 con selector de rol, tablero con refresco cada 5 s y descarga de CSV, cola de aprobación (motivo obligatorio, nivel por rol, separación de funciones, intento rechazado al acta, una sola respuesta por decisión), calendario, acta con verificación de cadena y detalle de factura. Núcleo mínimo del acta en SQLite (AC1 a AC7). Revisado a mano en el navegador. |
| 17 oct | *(commit anterior)* | Specs de `acta-y-csv`: 9 bloques de requisitos (AC1 a AC9), diseño con tabla de solo añadir, huellas, CSV y salas, y 10 tareas (AT1 a AT10). Faltan 2 specs. |
| 17 oct | `1d0a7d1` | Se crearon `AVANCES.md` y `CLAUDE.md`, para que cualquier chat nuevo de Claude Code conozca el proyecto, lo hecho, lo pendiente y lo que sigue. |
| 17 oct | `4ad15b4` | Se corrigieron las maquetas de «Ruta de una factura»: umbral de pago automático (3 M), motivo de la F-1045 y nivel de la F-1047 (persona, no senior). Presupuesto del periodo en **100 M**. PDF actualizado. |
| 17 oct | `77c9522` | Specs del motor de reglas: 11 bloques de requisitos, diseño y 15 tareas. Índice en `specs/README.md`. |
| 17 oct | *(análisis)* | Se estudió la documentación de feature specs de Kiro. Se decidió adoptar el **método** (requisitos EARS, diseño y tareas) en `specs/`, sin instalar Kiro. |
| 17 oct | `d9dff20` | Se subió la guía de las 6 alternativas actualizada: entrega a las 8:00, margen de ~17 h, plan por horas, Opción 6 reducida al enrutador de canal y sello público a futuro. |
| 17 oct | `2941e8c` | PDF de «Ruta de una factura» con la **sugerencia de canal de pago** (paso 8 del flujo, maqueta, tabla de canales) y la sección «A futuro». |
| 17 oct | *(decisión)* | Se compararon la guía de @Marcelo Linero y nuestro diseño. Se **confirmó la entrega: dom 18 oct 8:00 a. m.** (antes se creía 12:00 y se había dicho 20:00). |
| 16–17 oct | *(sin commits)* | Diseño construido en conversación: agente de reglas en lenguaje natural, agente de entrada con chat al proveedor, calendario de facturas esperadas, agente de conciliación, CSV y tablero, niveles persona/senior, dos paneles con sala, 8 maquetas, despliegue solo en Railway. «Jurado» pasó a llamarse **«motor de reglas»**. |
| 16 oct | `7f9c408` | Primer PDF de «Ruta de una factura» en `docs/`. |
| 16 oct | *(inicio)* | Repositorio creado por el equipo como **`Colombiadevs`** (se había pedido «Colombia Devs»; GitHub no admite espacios). Agregado a la sesión y clonado. |

## 7. Cambios pendientes

Cosas ya hechas que hay que **revisar, confirmar o corregir**:

| # | Pendiente | Quién / cómo |
|---|---|---|
| P1 | **Decisiones abiertas D1 a D5** de `specs/motor-de-reglas/requirements.md` (zona gris de 5 % a 10 %, qué cuenta en el gasto, periodo, preparador, valores por defecto) | El equipo las confirma. Hay propuesta por defecto |
| P2 | Se interpretó «aumenta el presupuesto 100M» como **fijarlo en 100 M**, no sumar 100 M (125 M) | Confirmar con el usuario |
| P3 | **Datos de Blinka:** los canales y monedas ya salen del sitio oficial (captura del 17 oct). Siguen sin verificar los **costos, tiempos y límites** de cada ruta (están como «sin dato» o «supuesto»), y las redes de USDC no se usan todavía | Verificar con Blinka si se quiere mostrar costos |
| P4 | **Nombres por verificar** antes de fijar dependencias: modelos (Haiku 5.5, Sonnet 5.5) y funciones de Streamlit (`st.query_params`, `st.fragment` con `run_every`) | Quien monte el entorno |
| P5 | «Ruta de una factura» **no tiene** una sección «Plan hasta la entrega». Solo está en la guía | Opcional: agregarla |
| P6 | **El PDF se genera a mano** desde la página en línea (Chromium, A3 horizontal). Si la página cambia, hay que regenerar y subir el PDF | Quien edite el diseño |
| P7 | Si se construye el sello público: confirmar con los organizadores que una **testnet no cuenta como mover dinero** | Solo si se retoma |
| P8 | Las fichas de la guía describen la **Opción 6 completa** a propósito. El alcance real es solo el enrutador | Ninguno, solo saberlo |
| P11 | Falta un chequeo atómico entre validar y escribir una aprobación (hoy la clave de idempotencia evita la doble respuesta). Al pasar a PostgreSQL, validar dentro de la transacción | A, al desplegar |
| P12 | El menú lateral de Streamlit muestra «Cola de aprobacion» sin tilde (sale del nombre del archivo). Cosmético | Opcional: `st.navigation` |
| P13 | El acta usa **SQLite**. Falta PostgreSQL con roles y permisos (AC1.2) para Railway, y no hay purga de salas (AC7.4) | Al desplegar (PT10) |
| P15 | **Calibración propia del motor** (D1 a D5 siguen abiertas): zona gris 5 % a 10 %, gasto cuenta solo lo pagado o aprobado, periodo = mes en Bogotá, y los ajustes de «Ajustes al construir». Las 20 facturas de `casos.yaml` se escribieron junto con el motor: **faltan casos trampa de otra mano** (D) para que `eval.py` mida de verdad | D y el equipo |
| P17 | **La lectura con IA no se probó con ninguna API real.** Claude: `messages.create` con `output_config.format`. Gemini: `generate_content` con `response_json_schema`. Los SDK aceptan la configuración, pero falta correr `python3 -m agents.probar` con una clave. **Los nombres de modelo por defecto no están verificados** (`gemini-2.5-flash`, `claude-sonnet-5-5`; se cambian con `MODELO_GEMINI` y `MODELO_ENTRADA`). `ENTRADA_MODO=demo` fuerza el modo demo | Quien tenga la clave (ET7) |
| P22 | Gemini en plan gratuito puede usar lo enviado para mejorar el producto: solo facturas ficticias. Un filtro de seguridad de Gemini puede bloquear una lectura (se trata como falla y se escala) | Saberlo |
| P20 | **Falta hacer el despliegue en Railway** (lo hace alguien con acceso a la cuenta; pasos en `README.md`): conectar el repositorio, agregar el volumen en `/data`, poner `ANTHROPIC_API_KEY` y `FECHA_DEMO=2026-10-17`, generar el dominio. Railway despliega una rama del repositorio: hoy el trabajo está en `claude/focused-dirac-iurhyp`, no en `main` | Quien tenga Railway |
| P21 | Con una sola réplica y SQLite no hay alta disponibilidad: un reinicio corta la demo unos segundos. Las salas viejas no se purgan (AC7.4) | Aceptado para la entrega |
| P18 | Las facturas de ejemplo dependen de la **fecha de hoy** (el calendario es de octubre de 2026 y la ventana es de ±5 días): la «normal» solo se paga sola entre el 9 y el 19 de octubre. Después saldrá «inesperada» y se escalará | Fijar la fecha de la demo si hace falta |
| P19 | El agente no pregunta por la cuenta bancaria (DE2): solo se compara con los registros. Las imágenes siempre se escalan por no tener segunda lectura (EA3.3) | El equipo decide si basta |
| P23 | **Specs de `main` sustituidas.** Las specs de `paneles-y-despliegue` (PD1 a PD12, PT1 a PT14) y de `extraccion-y-agente-de-entrada` que otra sesión subió a `main` (VER-0003) se reemplazaron por las de esta rama, que describen el código que existe. Siguen en el historial (`dc04e18`, `8bb35bb`). **El equipo debe confirmar cuáles specs valen**; la numeración y la interfaz pública del agente de entrada difieren | El equipo |
| P24 | Los commits anteriores de esta rama no pasaron por el `verificador` (la regla llegó a `main` después); se verificó la rama completa de una vez | Saberlo |
| P9 | **Decisiones abiertas DA1 a DA5** de `specs/acta-y-csv/requirements.md` (una fila por evento, cadena por sala, separador del CSV, reinicio de sala, sello público) | El equipo las confirma. Hay propuesta por defecto |
| P10 | **Decisiones abiertas EXD1 a EXD6** de `specs/extraccion-y-agente-de-entrada/requirements.md` (OCR o segunda llamada para imágenes, si la alerta de órdenes cambia la decisión, idiomas, varias facturas por archivo, modelo, reformular preguntas con IA) | El equipo las confirma. Hay propuesta por defecto |
| P11 | **Decisiones abiertas PDD1 a PDD6** de `specs/paneles-y-despliegue/requirements.md` (página de inicio, clave de demostración, refresco, rol administrador, OCR en Railway, idioma) | El equipo las confirma. Hay propuesta por defecto |

## 8. Próximas tareas

En orden. El detalle de cada tarea del motor está en `specs/motor-de-reglas/tasks.md`.

1. **Revisar y aprobar** las specs `motor-de-reglas` (resolver D1 a D5) y `acta-y-csv` (resolver DA1 a DA5).
2. ~~**Escribir las specs que faltan**~~: las 4 están en borrador. Falta que el equipo las **revise** (D1 a D5, DA1 a DA5, DP1 a DP3, DE1 a DE3).
3. **Hacer el despliegue en Railway** (P20) y abrirlo desde otro computador. Después, probar el agente con la clave real (ET7).
3b. Las páginas de reglas y resumen (PT11, capa 3), solo si sobra tiempo.
4. ~~**Ola 0 y Ola 1 del motor**~~ (T1 a T10, T13 a T15 hechas; ver registro). Pendiente del motor: T11 simular y T12 vigencias con conflictos y afloja/restringe (solo si se hace el agente de reglas).
5. **Que otra persona escriba casos trampa nuevos** (P15) y los pase por `eval.py`.
5b. **Escribir el pitch y el guion de la demo** con las skills `sales-narrative` y `storytelling` (aún no se ha escrito el pitch; solo están las skills).
6. **Control de las 18:00:** correr `eval.py`. Si los casos trampa pasan, el enrutador de canal (T7) ya está hecho; con tiempo, las piezas de la capa 3. Si no pasan, esas horas se usan para corregir el motor.

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
