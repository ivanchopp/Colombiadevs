# AVANCES

> **Si eres un chat nuevo de Claude Code, empieza aquí.** Este archivo es la memoria del proyecto: qué se quiere hacer, qué ya se hizo, qué falta y qué sigue. Léelo completo antes de tocar nada y **actualízalo al terminar cada cambio** (ver «Cómo mantener este archivo»).

**Última actualización:** sáb 17 oct 2026, 12:00 (hora Bogotá)
**Entrega:** **dom 18 oct 2026, 8:00 a. m. (hora Bogotá).** Objetivo: enviar a las 7:00.
**Repositorio:** https://github.com/ivanchopp/Colombiadevs (rama `main`, no hay otras)

---

## 1. En 30 segundos

- **Qué es:** un agente que revisa las facturas de una empresa y decide, para cada una, si **pagar, frenar o escalar a una persona**, siguiendo reglas que la empresa define. Explica cada decisión. **No mueve dinero real.**
- **De dónde viene:** el *Reto Blinka, «Agentes que pagan por la empresa»* (Hackathon 30X, HackRadar). Blinka es una fintech colombiana en EE. UU. con cuentas en USD y pagos a Latinoamérica.
- **Idea central:** la IA solo **lee y redacta**. Un programa normal, el **motor de reglas**, **decide**. Ante la duda, el resultado es **escalar, nunca pagar**.
- **Equipo:** 4 personas. Reparto sugerido: **A** motor y pruebas · **B** agentes con IA · **C** pantallas · **D** datos, evaluación y pitch.
- **Estado del código:** **todavía no hay código.** Hay documentos de diseño, una guía de plan y las specs del motor de reglas.

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
| `VERIFICACIONES.md`, `.verificaciones/` | Historial de verificaciones (no se edita a mano) |
| `specs/motor-de-reglas/` | `requirements.md` (53 criterios EARS), `design.md`, `tasks.md` (T1 a T15) |
| `specs/paneles-y-despliegue/` | Los dos paneles de la demo, la sala, los roles, el refresco, el despliegue en Railway, las protecciones y la prueba de humo. `requirements.md` (criterios PD), `design.md`, `tasks.md` (PT1 a PT14) |
| `specs/extraccion-y-agente-de-entrada/` | Agente de entrada con IA: recepción, extracción, segunda lectura, preguntas al proveedor, defensa contra órdenes escondidas y modo demo. `requirements.md` (criterios EX), `design.md`, `tasks.md` (ET1 a ET11) |
| `specs/acta-y-csv/` | Acta de solo añadir con huellas, CSV, tablero, salas y agente de conciliación. `requirements.md` (criterios AC), `design.md`, `tasks.md` (AT1 a AT10) |
| *(aún no existe)* `engine/`, `agents/`, `app/`, `data/`, `tests/`, `eval.py`, `init_db.py` | Estructura de código prevista |

## 6. Registro de cambios

Lo más reciente va arriba.

| Cuándo | Commit | Qué se hizo |
|---|---|---|
| 17 oct | *(este commit)* | Specs de `paneles-y-despliegue`: 12 bloques de requisitos (PD1 a PD12), diseño con la sala, los dos paneles, el refresco, Railway y la prueba de humo, y 14 tareas (PT1 a PT14). **Ya están las 4 specs.** |
| 17 oct | `7392522` | Se fusionó el PR #1 de otra sesión de Claude Code: skill **`verificador`** (`3d9b7b3`), `monto_para_nivel` alineado con R5.2 (`0aecd8a`) y aclaración de D2 (`0b5e422`). Quedaron registradas VER-0001 y VER-0002. |
| 17 oct | `8bb35bb` | Specs de `extraccion-y-agente-de-entrada`: 9 bloques de requisitos (EX1 a EX9), diseño con segunda lectura, plantillas de preguntas y defensa contra órdenes escondidas, y 11 tareas (ET1 a ET11). Se ajustó la spec del motor: R2.2, nuevo R2.5 y campos nuevos de la ficha. Falta 1 spec. |
| 17 oct | `8d91175` | Specs de `acta-y-csv`: 9 bloques de requisitos (AC1 a AC9), diseño con tabla de solo añadir, huellas, CSV y salas, y 10 tareas (AT1 a AT10). Faltan 2 specs. |
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
| P3 | **Datos de Blinka sin verificar.** El sitio `blinka.co` y el reto en `hackradar.30x.com` no se pudieron abrir desde el entorno de Claude. Los canales (USDC en varias redes, Bre-B, PSE) vienen de la guía. Otras fuentes hablaban de SPEI y Pix | Verificar en el sitio oficial |
| P4 | **Nombres por verificar** antes de fijar dependencias: modelos (Haiku 5.5, Sonnet 5.5) y funciones de Streamlit (`st.query_params`, `st.fragment` con `run_every`) | Quien monte el entorno |
| P5 | «Ruta de una factura» **no tiene** una sección «Plan hasta la entrega». Solo está en la guía | Opcional: agregarla |
| P6 | **El PDF se genera a mano** desde la página en línea (Chromium, A3 horizontal). Si la página cambia, hay que regenerar y subir el PDF | Quien edite el diseño |
| P7 | Si se construye el sello público: confirmar con los organizadores que una **testnet no cuenta como mover dinero** | Solo si se retoma |
| P8 | Las fichas de la guía describen la **Opción 6 completa** a propósito. El alcance real es solo el enrutador | Ninguno, solo saberlo |
| P9 | **Decisiones abiertas DA1 a DA5** de `specs/acta-y-csv/requirements.md` (una fila por evento, cadena por sala, separador del CSV, reinicio de sala, sello público) | El equipo las confirma. Hay propuesta por defecto |
| P10 | **Decisiones abiertas EXD1 a EXD6** de `specs/extraccion-y-agente-de-entrada/requirements.md` (OCR o segunda llamada para imágenes, si la alerta de órdenes cambia la decisión, idiomas, varias facturas por archivo, modelo, reformular preguntas con IA) | El equipo las confirma. Hay propuesta por defecto |
| P11 | **Decisiones abiertas PDD1 a PDD6** de `specs/paneles-y-despliegue/requirements.md` (página de inicio, clave de demostración, refresco, rol administrador, OCR en Railway, idioma) | El equipo las confirma. Hay propuesta por defecto |

## 8. Próximas tareas

En orden. El detalle de cada tarea del motor está en `specs/motor-de-reglas/tasks.md`.

1. **Revisar y aprobar** las specs `motor-de-reglas` (resolver D1 a D5) `acta-y-csv` (resolver DA1 a DA5) y `extraccion-y-agente-de-entrada` (resolver EXD1 a EXD6) y `paneles-y-despliegue` (resolver PDD1 a PDD6).
2. **Escribir las specs que faltan** (máx. 90 min en total, sin repetir el diseño): ~~`acta-y-csv`~~, ~~`extraccion-y-agente-de-entrada`~~ y ~~`paneles-y-despliegue`~~ (**las 4 specs ya tienen borrador**).
3. **Despliegue de prueba en Railway (tarea PT1, antes que cualquier pantalla):** app mínima que lea la clave, llame al modelo una vez y guarde una fila. Abrirla desde otro computador.
4. **Ola 0 del motor:** T1 modelos y esquemas (A), T2 datos semilla (D), T3 20 casos de prueba con decisión esperada (D).
5. **Ola 1:** T4 entrada y frenar, T5 beneficiario, montos y niveles, T10 cargar reglas. Luego T8 orquestador, T9 guardarraíl, T13 pruebas de propiedades, T14 `eval.py`, T15 conexión con el acta.
6. **Control de las 18:00:** correr `eval.py`. Si los casos trampa pasan, se suma el enrutador de canal (T7) y, con tiempo, las piezas de la capa 3. Si no pasan, esas horas se usan para corregir el motor.

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
