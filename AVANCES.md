# AVANCES

> **Si eres un chat nuevo de Claude Code, empieza aquí.** Este archivo es la memoria del proyecto: qué se quiere hacer, qué ya se hizo, qué falta y qué sigue. Léelo completo antes de tocar nada y **actualízalo al terminar cada cambio** (ver «Cómo mantener este archivo»).

**Última actualización:** sáb 17 oct 2026, 20:30 (hora Bogotá)
**Entrega:** **dom 18 oct 2026, 8:00 a. m. (hora Bogotá).** Objetivo: enviar a las 7:00.
**Repositorio:** https://github.com/ivanchopp/Colombiadevs · rama `main` (último: PR #14, commit `8510675`). El trabajo nuevo se hace en una rama y entra por PR, después de pasar por el `verificador`.

---

## 1. En 30 segundos

- **Qué es:** un agente para las **empresas clientes de Blinka**. Revisa las facturas de sus proveedores y decide, para cada una, si **pagar, frenar o escalar a una persona**, siguiendo las reglas que la empresa define. Explica cada decisión y, al final, entrega a Blinka un **archivo con las facturas aprobadas** para que Blinka haga los pagos desde la cuenta del cliente. **Nosotros no movemos dinero real:** somos la capa de control antes del pago. (Enfoque aclarado por Blinka el 17 oct; ver la sección 1b.)
- **De dónde viene:** el *Reto Blinka, «Agentes que pagan por la empresa»* (Hackathon 30X, HackRadar). Blinka es una fintech colombiana en EE. UU. con cuentas en USD y pagos a Latinoamérica.
- **Idea central:** la IA solo **lee y redacta**. Un programa normal, el **motor de reglas**, **decide**. Ante la duda, el resultado es **escalar, nunca pagar**.
- **Equipo:** 4 personas. Reparto sugerido: **A** motor y pruebas · **B** agentes con IA · **C** pantallas · **D** datos, evaluación y pitch.
- **Estado del código (en `main`):** funciona de punta a punta el **motor de reglas**, el **acta** (SQLite), el **agente de entrada** y los **dos paneles** (Streamlit). **298 pruebas pasan** y `python3 eval.py` da **29 de 29, con 0 pagos indebidos** (rama de R2 y R3 fusionada con `main` `8510675`). Cada cambio pasa por la skill `verificador` (última: VER-0033). *(En `main` son 240 pruebas y 20 casos: R2 y R3 están en la rama `claude/friendly-cerf-aygx2r`, sin PR.)*
- **Desplegado:** https://colombiadevs-production.up.railway.app/ (probado con el commit `014409d`; **no se ha confirmado que Railway corra el último `main`**, PR #16, que cambia los proveedores de los ejemplos: revisar el commit en `?diagnostico=1`). El 17 oct se comprobó desde fuera: `/_stcore/health` responde `ok`, `?diagnostico=1` muestra Gemini activo (`gemini-2.5-flash`), `GEMINI_API_KEY` definida y `FECHA_DEMO=2026-10-17`. Con los botones de ejemplo, el Panel 1 devolvió «Resuelta» para la normal y la repetida, y «En revisión» para la de orden escondida; el acta de esa sala verificó 10 de 10 filas.
- **Lo que NO está probado:**
  1. **La lectura con IA sobre un archivo propio.** Gemini lee los textos de ejemplo en Railway, pero falta subir un PDF o una foto y revisar que la ficha salga bien (P17). Claude como proveedor tampoco se probó.
  2. **La decisión exacta de cada factura en producción.** Se vio el estado en el Panel 1, pero no `PAGAR`/`FRENAR`/`ESCALAR` de cada una en el tablero de Railway, ni que el acta sobreviva a un reinicio del servicio (volumen en `/data`).
- **No existen todavía:** el agente de reglas en lenguaje natural, el agente de conciliación y la página de resumen (capa 3), PostgreSQL con permisos, y las vigencias con conflictos (T12).
- **Proveedores válidos:** el motor decide con el listado de **156 proveedores válidos** (`data/proveedores.yaml`). Los casos de prueba, el calendario, las facturas de muestra y la semilla de la demo usan proveedores de ese listado (tabla de migración en `specs/ordenes-de-compra/design.md`).
- **Órdenes de compra (R3, versión mínima en el motor + OT5):** la revisión OC4 decide con la orden de compra (inexistente, ajena o con otro NIT → senior; ya facturada o más de 10 % → frenar; de 5 % a 10 % → persona; un proveedor marcado → senior) y **el agente de entrada ya lee el número de OC y el NIT de la factura** (IA y patrones, comparados en la segunda lectura). El Panel 1 ofrece 3 muestras con OC. **Las órdenes son sintéticas** (`data/ordenes_compra.yaml`, 7 órdenes de proveedores válidos escritas por nosotros): el archivo real sigue bloqueado por OCD13. Faltan OT7 (página de órdenes), la columna en `facturas.csv` y el importador del `.xlsx` real. **Railway debe redesplegarse** para ver las muestras nuevas.
- **Para verlo:** `pip install -r requirements.txt` y `streamlit run app/Panel_1_Proveedor.py`. **Control de las 18:00:** `python3 eval.py`.

## 1b. Reunión con Blinka (sáb 17 oct 2026, 17:02)

Blinka habló con el equipo. **Lo que se dijo es la fuente de verdad del producto.**

**Decisiones y aclaraciones**

1. **El usuario es el cliente de Blinka**, no el equipo interno de Blinka. Se corrigió la premisa con la que el equipo había empezado. El producto automatiza y optimiza las compras de empresas que tienen su cuenta en Blinka y le pagan a sus proveedores.
2. **Arquitectura de salida (decisión acordada):** el sistema genera un **archivo de salida con las facturas aprobadas**, automática o manualmente; **Blinka hace los pagos** a los proveedores desde la cuenta del cliente. Blinka lo confirmó.
3. **Entrada:** facturas electrónicas válidas de varios países (en XML, PDF o foto), verificadas con la autoridad tributaria (DIAN en Colombia, SUNAT en Perú) y revisadas con las reglas de finanzas. Cada proveedor tiene su propio formato.
4. **Órdenes de compra:** validar la factura contra la orden de compra y los datos del cliente o proveedor en el ERP, por archivo o por API. En Colombia aplican normas de cumplimiento como Sarlaft.
5. **Contratos:** los clientes tienen estructuras de pago complejas basadas en contratos. Se sugirió **subir el contrato con la estructura y la cadencia de pagos** para agendarlos solos.
6. **MCP:** Blinka lanzó la semana pasada un servidor MCP para conectarse a sistemas de IA como GPT y **programar pagos con un comando de texto**. En la reunión se dijo que el equipo ya trabajaba en **ajustar reglas de pago con lenguaje natural**.
7. **Moneda y contabilidad:** los clientes operan hoy **en dólares** y llevan la contabilidad en Blinka o la conectan a sistemas como QuickBooks.
8. **Criptomonedas:** los pagos internacionales y los de Bre-B se ejecutan con cripto por debajo, pero se dijo que eso **«se sale un poco del alcance principal»**. Marcelo añadió que otros medios de pago son un extra de innovación y que primero se resuelve la necesidad principal.
9. **Idea para el pitch:** productizar y «agentizar» un **equipo de compras de unas 10 personas** que analiza proveedores y centros de costos.

**Cómo encaja lo que ya existe**

| Lo que dijo | Lo que tenemos |
|---|---|
| Reglas de finanzas sobre cada factura; aprobación automática o manual | Motor de reglas con dos niveles de aprobación y acta verificable |
| La IA no decide | Es nuestra regla central |
| Leer PDF y foto; cada proveedor con su formato | Lectura con IA (Gemini o Claude), segunda lectura sin IA y respaldo por patrones (ampliado el 17 oct para facturas electrónicas colombianas) |
| Validar contra órdenes de compra | Revisión OC4 en el motor con órdenes sintéticas (R3); falta que el agente lea la OC de la factura y cargar las órdenes reales |
| Ajustar reglas en lenguaje natural | Página de reglas por formulario, con vista previa y afloja/restringe; falta la capa de lenguaje natural |
| Rutas de pago de Blinka | Recomendación de canal (Bre-B, SPEI, Pix, USDC…), solo sugerencia |
| Presupuesto | `presupuesto_periodo`; falta por centro de costos |

**Dónde fallamos hoy** (todo está en el roadmap de la sección 8b)

- ~~No existía el **archivo de salida con las facturas aprobadas**~~ (**hecho el 17 oct, R1**: `pagos_aprobados.csv` en la página Acta del Panel 2). `facturas.csv` y `eventos.csv` siguen siendo de auditoría y no traen la cuenta de destino.
- Nuestros textos hablaban de «una empresa» y del equipo de finanzas; hay que contar el producto como la capa de control de los clientes de Blinka. **Panel 1 (proveedor) es solo una entrada de demostración**; en el producto real las facturas llegan al cliente.
- Las **órdenes de compra** no entran aún al motor.
- ~~La moneda base era COP y los clientes operan en USD~~ (**hecho el 17 oct, R4**: la base de la demo es USD).
- No leemos **XML**, ni validamos el NIT ni consultamos a la DIAN.
- No hay nada de **contratos**, ni de **Sarlaft**, ni de **centros de costos**.
- **Compromiso hecho en la reunión que no está cumplido:** se dijo que ya se trabajaba en cambiar las reglas con lenguaje natural, y **no existe** (P29).

**Fuera de alcance, por decisión de Blinka:** mover dinero y las criptomonedas como foco. La ruta USDC queda como una sugerencia más, sin trabajo extra.

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
| **Núcleo** | Lectura de facturas con segunda lectura, motor de reglas con dos niveles de aprobación (persona y senior), acta con cadena de huellas, CSV y tablero, cola de aprobación, Panel 1, un test por caso trampa, despliegue en Railway | Sáb 18:00 | **Hecho**, salvo la lectura con IA sobre archivos propios (P17) y confirmar las decisiones en el tablero de Railway (P18) |
| **Capa 2** | Sugerencia de canal de pago con las rutas de Blinka (Bre-B, SPEI, Pix, SEPA, transferencias locales, rutas en USD, ACH y wire, SWIFT, USDC), solo recomendación | Sáb 18:00 a 21:00, si el control de las 18:00 pasa | **Hecho** |
| **Capa 3** | Calendario de facturas esperadas, agente de reglas en lenguaje natural (con vigencias y detección de afloja/restringe), simular cambios, chat con el proveedor, agente de conciliación | Solo si sobra tiempo | Calendario y chat con el proveedor: **hechos**. Simular (T11) y afloja/restringe (parte de T12): **hechos** en la página de reglas. Agente de reglas en lenguaje natural, vigencias con conflictos y conciliación: **no** |
| **A futuro** | Sello público del registro (raíz Merkle por lote anclada en testnet); billetera on-chain (Opción 5 de la guía), solo como visión en el pitch | No se construye | — |

**Alcance nuevo de la reunión con Blinka (17 oct 17:02):** archivo de salida, órdenes de compra, USD, XML, contratos, lenguaje natural, Sarlaft, centros de costos y ERP. Está en el roadmap de la sección 8b, por fases.

**Orden para recortar** si algo se atrasa: agente de conciliación → chat con el proveedor → calendario → agente de reglas (dejar edición por formulario o YAML) → enrutador de canal. La Opción 1 sola ya cumple el entregable y los tres criterios.

## 4. Cómo funciona (resumen)

**Actores:**
- **Agente de entrada (IA):** recibe la factura, la lee (Gemini o Claude), pregunta al proveedor lo dudoso (máx. 2 turnos) y entrega una **ficha** estándar con el dato original y el aclarado. Una **segunda lectura** simple (patrones de texto) verifica a la IA, y otra detección sin IA busca órdenes escondidas. Spec en `specs/extraccion-y-agente-de-entrada/`.
- **Motor de reglas (código, sin IA):** compara la ficha con los registros de la empresa, el calendario y las reglas vigentes. Decide `PAGAR`, `FRENAR` o `ESCALAR`, el nivel de aprobación, y sugiere un canal de pago. Spec en `specs/motor-de-reglas/`.
- **Agente de reglas (IA) — no construido:** convertiría una instrucción en lenguaje normal en un cambio de reglas, con vista previa y confirmación.
- **Agente de conciliación (IA) — no construido:** leería el acta (solo lectura), resumiría el periodo y avisaría de rarezas. No calcularía cifras.
- **Acta:** registro de solo añadir; cada fila lleva la huella de la anterior. De ahí salen el CSV y el tablero.
- **Persona de finanzas / senior de finanzas:** aprueban lo escalado según su nivel. Solo el senior aprueba lo de mayor riesgo y firma los cambios que *aflojan* una regla (página de reglas).
- **Evaluadores de la demo:** hacen de proveedor en el Panel 1 y revisan en el Panel 2.

**Decisiones del motor** (parámetros de demostración en **USD**, todos «supuesto»; equivalen a los antiguos en pesos con 1 USD = 4.000 COP):
- **Pagar:** todo OK, sin avisos y monto del periodo para ese beneficiario ≤ **3 M** (pago automático).
- **Frenar:** factura repetida, monto que supera lo acordado en más de **10 %**, sin presupuesto, o supera el techo duro (**12.500 USD**).
- **Escalar:** cualquier duda. Nivel **persona** hasta **2.500 USD**; **senior** por encima de 2.500 USD o si hay riesgo (beneficiario nuevo, cuenta distinta, límite por periodo de **3.750 USD** por beneficiario). Entre 5 % y 10 % sobre lo acordado: persona.
- **Presupuesto del periodo:** **25.000 USD**. Moneda base: USD (configurable en `reglas.yaml`). Tolerancia normal: 5 %.

**Demo con dos paneles** que comparten una *sala* (un código por visitante en el enlace):
- **Panel 1, proveedor (abierto):** chat con el agente de entrada, subir PDF/foto/correo/TXT, cuatro archivos de muestra descargables (sin botones que elijan el caso: el sistema lee y decide) y estado de la factura. **Nunca muestra reglas ni límites.**
- **Panel 2, finanzas (con rol):** tablero con detalle de cada factura, cola de aprobación, calendario, acta y **reglas** (ver, editar, vista previa y firma del senior para aflojar). *(El chat de reglas y el resumen de conciliación no están construidos.)*

**Tecnología real:** Python 3.12 (`.python-version`, `Dockerfile`), **Gemini (`google-genai`) o Claude (`anthropic`)** para leer facturas, Pydantic, Streamlit (varias páginas), **SQLite** (en un volumen de Railway; PostgreSQL pendiente), pandas para el CSV, pytest y Hypothesis, imagen de Docker desplegada en **Railway**. Sin frameworks de agentes pesados.

## 5. Mapa del repositorio

| Ruta | Qué es |
|---|---|
| `AVANCES.md` | Este archivo |
| `CLAUDE.md` | Indicaciones cortas para Claude Code |
| `README.md` | Cómo correr, probar y desplegar; variables de entorno; Gemini o Claude |
| `docs/guion-demo.md` | **Guion de la demo y el pitch** (4 a 5 min): la capa de control de los clientes de Blinka, solo lo que existe hoy, preguntas probables y lo que no se dice |
| `docs/Ruta-de-una-factura.pdf` | **Diseño general:** actores, flujo, maquetas, herramientas, despliegue, a futuro. Se genera de una página en línea privada del equipo |
| `docs/Guia-6-alternativas-actualizada.pdf` | Guía de las 6 alternativas de @Marcelo Linero, ajustada a la entrega de las 8:00, con plan por horas |
| `specs/README.md` | Índice y reglas de las especificaciones |
| `specs/motor-de-reglas/` | 53 criterios EARS (R1 a R11), `design.md` (con «Ajustes al construir»), tareas T1 a T15 |
| `specs/acta-y-csv/` | 51 criterios (AC1 a AC9), diseño, tareas AT1 a AT10 |
| `specs/archivo-de-salida/` | **Alcance nuevo de la reunión con Blinka.** Archivo de salida con las facturas aprobadas que Blinka paga. Criterios AS1 a AS4, diseño y tareas AST1 a AST4 (**hechas**: `acta/exportar_pagos.py`, columnas supuestas, P30) |
| `specs/ordenes-de-compra/` | **Alcance nuevo.** Órdenes de compra autorizadas antes de la factura y registro de proveedores con NIT/RFC/RUC. Criterios OC1 a OC8, diseño, tareas OT1 a OT7 (OT1 parcial, OT2, OT3 y OT6 hechas con órdenes sintéticas; OT4 parcial), 13 decisiones (9 abiertas) |
| `specs/paneles-y-despliegue/` | Criterios PP1 a PP8 y PD1 (despliegue), diseño, tareas PT1 a PT12 |
| `specs/extraccion-y-agente-de-entrada/` | Criterios EA1 a EA9 y EA2b (proveedor intercambiable), diseño, tareas ET1 a ET8 |
| `.claude/skills/verificador/` | Skill que revisa cada cambio, lo aprueba o rechaza y lo registra. **Úsala antes de commitear.** |
| `VERIFICACIONES.md`, `.verificaciones/` | Historial de verificaciones (no se edita a mano) |
| `engine/` | Motor de reglas (sin IA): `modelos`, `evaluar`, `revisiones/` (entrada, frenar, beneficiario, montos, calendario), `niveles`, `canales`, `guardarrail`, `contexto` (desde el acta), `reglas_io` (incluye reglas por sala y validación de cambios), `simular` |
| `acta/` | Acta en SQLite: huellas, escribir, verificar, estado, CSV, `exportar_pagos` (archivo de salida para Blinka), tablero, salas. `esquema_postgres.sql` viene de otra sesión y **no se usa** todavía |
| `agents/` | Agente de entrada: `archivo`, `lectura_ia` (Gemini o Claude), `segunda_lectura` y `seguridad` (sin IA), `aclaraciones`, `estado`, `flujo`, `ejemplos`, `probar` |
| `app/` | Streamlit. `Panel_1_Proveedor.py`, `pages/` con el Panel 2 (Tablero, Cola de aprobación, Calendario, Acta, Reglas), `comun.py`, `apoyo.py` |
| `data/` | `reglas.yaml`, `techos.yaml`, `proveedores.yaml` (lista permitida), `registros.yaml` (acuerdos e historial), `tasas.yaml`, `canales.yaml`, `calendario.csv` y `casos.yaml` (20 facturas de prueba), todo «supuesto»; `demo_semilla.py`; `facturas_ejemplo/`; `importar_compras.py` (genera `proveedores.yaml` desde el Excel del equipo) |
| `eval.py` | Mide autonomía, seguridad (pagos indebidos = 0) y explicabilidad con los 29 casos |
| `tests/`, `pytest.ini` | 266 pruebas (`python3 -m pytest -q`), incluida la de propiedades con Hypothesis |
| `Dockerfile`, `railway.toml`, `requirements-prod.txt`, `requirements.txt`, `.env.example`, `.streamlit/config.toml` | Despliegue y dependencias. La imagen corre como root a propósito (volúmenes de Railway) |

## 6. Registro de cambios

Lo más reciente va arriba.

| Cuándo | Commit | Qué se hizo |
|---|---|---|
| 17 oct | *(este commit)* | **OT5: el agente de entrada lee la orden de compra y el NIT de la factura (OC3, EA2.5, EA3.9).** Spec primero en `extraccion-y-agente-de-entrada` y `ordenes-de-compra` (sección «OT5»). `lectura_ia`: el esquema suma `orden_compra` e `id_tributaria` (nunca dudosos); `segunda_lectura`: patrones de OC y NIT y comparación (la IA que inventa una OC que el texto no trae da `no_coincide`); `flujo`: la ficha los lleva. Tres muestras nuevas con OC en el Panel 1 y la obligación `O9` en el calendario para que la que cuadra se pague sola. **Arreglo aparte:** la prueba de propiedades encontró que un monto como `1E100` hacía lanzar `InvalidOperation` al motor (ya pasaba en `main`); ahora escala (R1.3). 32 pruebas nuevas (31 de OT5 y 1 del monto absurdo), 3 mutaciones detectadas. 298 pruebas, `eval.py` 29/29, 0 pagos indebidos. |
| 17 oct | `86f5024` | **Fusión de `main` (PR #18) y apertura del PR.** `main` sumó la revisión de la documentación tras el PR #14. Se conservó su VER-0027 y las verificaciones de esta rama pasaron otra vez de número (**VER-0028** a **VER-0031**); esta fusión es **VER-0032**. Sin cambios de código.
| 17 oct | `6ec6a2a` | **Fusión de `main` (R1 y R4) en la rama de R2 y R3.** `main` sumó el archivo de salida (R1) y la moneda base en USD (R4, PR #14). Se combinaron los imports de `frenar.py`; el calendario de los casos de OC pasó a USD (COP × 0,00025) porque la base ya no es el peso; y `OrdenCompra.moneda` dejó de tener «COP» por defecto, porque la prueba R5.6 prohíbe suponer la moneda en el código. Los IDs de verificación chocaron otra vez (VER-0024 a VER-0026 de `main`): los de esta rama pasan a **VER-0028** (R2), **VER-0029** (R3), **VER-0030** (fusión de `1764f22`) y **VER-0031** (esta fusión). 266 pruebas, `eval.py` 29/29, 0 pagos indebidos. |
| 17 oct | `1764f22` | **Fusión de `main` en la rama de R2 y R3.** `main` había migrado el motor a los 156 proveedores válidos mientras esta rama añadía las órdenes de compra: se adoptó la carga de `main` (`registros_de_proveedores` en `reglas_io`) y se quitó la copia propia; las 7 órdenes sintéticas, los casos y las pruebas se reasignaron a proveedores válidos (nombre y NIT iguales, ID nuevo); el caso de proveedor con identificación inválida pasó a una prueba con una marca puesta a mano, porque el listado de válidos no trae ninguno marcado (29 casos en vez de 30). Los IDs de verificación chocaron (VER-0021 y VER-0022 en ambas ramas): los de `main` conservan su ID y los de esta rama pasaron a **VER-0028** (R2), **VER-0029** (R3) y **VER-0030** (esta fusión) tras sucesivos choques con `main`. 244 pruebas, `eval.py` 29/29, 0 pagos indebidos. |
| 17 oct | `9202506` | **R3: órdenes de compra en el motor, versión mínima (OT2, OT3, OT6; OT4 parcial).** Spec primero: `design.md` gana «Ajustes al construir» y `tasks.md` el estado. Código: `Ficha` con `orden_compra` e `id_tributaria`; `engine/compras.py` (cargar y validar proveedores y órdenes, número normalizado, estado «facturada» desde el acta); `engine/revisiones/orden_compra.py` (OC4.1 a OC4.9) después de R4, y `frenar.acuerdo` deja que una OC que cuadra haga las veces de acuerdo. Un proveedor marcado va al senior aunque no cite OC. Una OC válida **no reemplaza el calendario** (OC4.9). `data/ordenes_compra.yaml` es **sintético**. Casos nuevos en `casos.yaml`; `eval.py` soporta `calendario_extra` y `oc_facturadas`. Verificado en VER-0029. |
| 17 oct | `ea0e355` | **R2: guion de la demo y el pitch** (`docs/guion-demo.md`). Cuenta el producto como la capa de control antes del pago de los clientes de Blinka, con un recorrido por minutos sobre los archivos de muestra del Panel 1 y el Panel 2, lo que sigue dicho como siguiente paso, preguntas probables y lo que no se dice. Los resultados exactos de cada archivo de muestra se confirman en el ensayo. Sin cambios de código. Verificado en VER-0028. |
| 17 oct | `f1d88f4` | **Revisión tras el PR #14 y análisis de 4 facturas XML de ejemplo.** Se volvió a correr la suite (240 pruebas) y `eval.py` (20/20, 0 pagos indebidos) sobre `8510675` y se corrigió lo que el PR #14 dejó atrás en este archivo: cabecera (PR #14), fecha de la comprobación, estado de `specs/archivo-de-salida/` en el mapa y el commit de R4. El equipo compartió 4 facturas XML (PO-2026-001, 002, 003 y 005): se analizaron sin subirlas al repositorio y se registró P33 con lo encontrado. Sin cambios de código. |
| 17 oct | `890ecb9` | **R4: moneda base USD y configurable (R5.6 a R5.8).** Los clientes de Blinka operan en dólares, así que la base de la demo pasa de COP a **USD**. Es un cambio de escala uniforme (1 USD = 4.000 COP, supuesto): `reglas.yaml` (750 / 2.500 / 12.500 / 3.750 / 25.000), `techos.yaml`, `tasas.yaml` (a USD), `calendario.csv` y los montos base de `registros.yaml` y `casos.yaml`. **Las decisiones de las 20 facturas no cambian** (20 de 20, 0 pagos indebidos). Ya no queda «COP» fijo: los textos del motor, el tablero (que además usaba un presupuesto propio de 100 M y ahora usa el de las reglas), la cola y la página de reglas usan la moneda base configurada. **Regla nueva R5.7:** si la tabla de cambio no da 1 para la moneda base, el motor escala al senior y nunca paga. 5 pruebas nuevas (238) y 2 mutaciones detectadas; se ajustaron las pruebas que tenían montos en pesos. Con montos en USD los centavos pesan: una factura 1 COP por encima del 10 % ya no se distingue (se redondea a centavos de USD). **No afloja ninguna regla.** |
| 17 oct | `2554db8` | **R1: archivo de salida `pagos_aprobados.csv` (AS1 a AS4, AST1 a AST4).** Nuevo `acta/exportar_pagos.py`: genera, solo desde el acta, la instrucción de pago para Blinka con las facturas en estado `PAGADA` (aprobadas por el motor o por una persona). La cuenta de destino sale del **registro de la empresa**, nunca de la factura ni del chat; una aprobada sin cuenta registrada queda fuera y se avisa. Antes de generar se verifica la cadena de huellas; sin cadena válida no hay archivo. Columnas (supuesto, P30): lote, factura, número, beneficiario, identificación tributaria, cuenta, monto y moneda de la factura, monto base, canal, orden de compra, tipo de aprobación (automática o manual), quién aprobó, hora, fila del acta y huella. Neutraliza fórmulas, usa `Decimal` y marca `supuesto`. Botón y resumen (cantidad y total por moneda) en la página Acta del Panel 2, con el aviso de que el sistema no mueve dinero. 17 pruebas nuevas (233) y 5 mutaciones detectadas (sin filtro de estado, cuenta de la ficha, sin cuenta igual entra, sin guarda de ficha inválida, todo automático). **No cambia ninguna decisión del motor.** Pendiente: `id_tributaria` y `orden_compra` salen vacías hasta que entren las órdenes de compra (R3). |
| 17 oct | `c8dd76f` | **Revisión total de la documentación tras el PR #16.** Se corrió de nuevo la suite (218 pruebas) y `eval.py` (20/20, 0 pagos indebidos) y se alineó la documentación con el código: cabecera y mapa de este archivo (PR #16, 218 pruebas, OT2 parcial, 9 decisiones abiertas de órdenes de compra, control de las 18:00 cumplido), `README.md` (el despliegue en Railway y la lectura con Gemini sí se probaron), estado de `specs/README.md`, ET3, ET7 y ET8, PT7 y PT10, la trazabilidad del motor (apuntaba a archivos de prueba que no existen) y OCD3 marcada como aplicada. Se agregó P32 (Railway puede no correr el último `main`). Sin cambios de código. |
| 17 oct | `fb204db` | **El motor usa los proveedores válidos (OCD4, OT2 parcial).** Spec primero (OC1.6 y OCD4 resuelta: reemplazar). `cargar_contexto_base` toma la lista permitida, la cuenta y el país de `proveedores.yaml`, y los acuerdos e historial de `registros.yaml` (que ya no lista beneficiarios; si nombra a un proveedor inexistente, la carga falla). Los 9 beneficiarios de ejemplo pasaron a proveedores válidos del mismo país o moneda (Brasil y Alemania, que no están en el listado, pasaron a Perú y Ecuador; los montos de Brasil se convirtieron a PEN). Se actualizaron los 20 casos de prueba, el calendario, las 4 facturas de muestra, las lecturas guardadas del modo demo, la semilla de la demo, el README y las pruebas. Mismas decisiones que antes: semilla, muestras y `eval.py` 20/20 con 0 pagos indebidos. 218 pruebas. La demo desplegada toma los cambios al redesplegar desde `main`; las salas ya creadas conservan sus nombres anteriores (el acta no se modifica). |
| 17 oct | `a833638` | **Listado de proveedores válidos.** El equipo entregó el listado definitivo de proveedores válidos (156: 40 de Colombia, 40 de Ecuador, 39 de Perú y 37 de México) y pidió eliminar los demás. `data/proveedores.yaml` se regeneró solo con ellos: sale el resto del listado de 200, incluidos los 30 con identificación repetida o inválida, y ninguno queda marcado. Eso resuelve OCD5 y OCD11. **Hallazgo nuevo (OCD13):** ninguno de los 30 proveedores de las órdenes de compra está entre los válidos, así que sus órdenes no se pueden cargar todavía. El motor sigue sin usar este registro (OT2). `registros.yaml` (los 9 beneficiarios del motor) no cambia. |
| 17 oct | `65fcb0f` | **Documentación puesta al día con la reunión con Blinka (17:02).** Se registró en `AVANCES.md` (secciones 1, 1b y 3) lo que se dijo en la reunión, cómo encaja con lo que ya existe y dónde fallamos; se reescribió el enfoque a «clientes de Blinka» (en `AVANCES.md` y `README.md`); se agregó el **roadmap** (sección 8b, R1 a R14, por fases) y los pendientes P29 a P31. **Spec nueva** `specs/archivo-de-salida/` (requisitos AS1 a AS4, diseño y tareas AST1 a AST4) para el archivo de salida de pagos aprobados, sin programar. Después se quitaron las notas de Gemini, y el **agente de reglas en lenguaje natural pasó a la fase 1** (R7; contratos quedó R8). Sin cambios de código. |
| 17 oct | `07b4849` | **Panel 1 sin botones de ejemplo (PP2.4, PP2.5, EA8.4).** Se quitaron los 4 botones que registraban una factura con lecturas guardadas: ahora la única entrada es subir un archivo, el sistema lo lee y el motor decide si es normal, repetida, de beneficiario nuevo o con orden escondida. Se agregó «Archivos de muestra (ficticios)» con los 4 archivos descargables y rótulos neutros (proveedor y número, sin decir el caso; la guía está en el `README.md`). Las lecturas guardadas quedan solo para pruebas y `eval.py`. **Consecuencia:** sin IA los archivos se leen con patrones y siempre se escalan, así que el caso «normal» solo llega a `PAGAR` con la IA activa (Gemini en Railway), y eso sigue sin probarse con un archivo real (P17). 4 pruebas nuevas (216). |
| 17 oct | `bb0f497` | **Patrones de respaldo para facturas electrónicas colombianas (EA3.4 a EA3.8).** Se probó con una factura electrónica colombiana real (restaurante) en modo demo: los patrones sacaron «ELECTR» como número y nada más, así que la factura quedó en revisión manual con todo sin leer. Ahora reconocen «TOTAL:» (valor en la línea siguiente, el último, sin confundir SUBTOTAL ni «TOTAL Base Imponible»), «Razón social/Nombre:» (el primero es el emisor), «Nro. Doc.:» y la moneda cuando solo aparece un código (el «COP» del total en letras; nunca se supone). El número exige algún dígito. Lo que no se encuentra, como el vencimiento de una factura de contado, sigue sin leer y se le pregunta al proveedor. Con la factura de prueba: beneficiario, número, monto y moneda bien leídos, falta solo el vencimiento. Sigue marcada como lectura dudosa, así que siempre se escala (EA8.2). 7 pruebas nuevas (212) y 2 mutaciones detectadas. Importante: esto mejora solo el respaldo y la segunda lectura; **no prueba la lectura con Gemini sobre ese PDF**. |
| 17 oct | `81bff8b` | **Prueba del despliegue en Railway.** El equipo desplegó la app y puso `GEMINI_API_KEY` y `FECHA_DEMO`. Se probó desde fuera (la red de la sesión tuvo que permitir el host): salud `ok`, diagnóstico con Gemini activo, tres botones de ejemplo (normal, repetida, orden escondida) leídos con la IA real y vistos en el Panel 1 sin errores, acta con cadena verificada (otra sala usó también «Beneficiario nuevo», sin revisar su resultado). Cierra P20 y la parte de P18 que dependía de `FECHA_DEMO`; P17 queda abierto solo para archivos propios. Se gastaron unas 7 lecturas de Gemini en dos salas de prueba. Sin cambios de código. |
| 17 oct | `28863cb` | **Arreglo: una factura «en revisión manual» ya aparece en el tablero (R8.6, PP5.7, EA6.2, EA2b.9).** Fallo real que reportó el equipo: si el agente no lograba armar una ficha completa (la IA falló o no leyó el monto y el proveedor no lo aclaró), el proveedor veía «en revisión manual» pero la factura **no se registraba en el acta**, así que finanzas no la veía. Ahora se registra como `ESCALAR` / `SENIOR` con su motivo (`ficha_invalida`), aparece en el tablero con el monto «sin leer» y en la cola del senior, **no entra al historial del motor y no se puede aprobar**: la cola solo ofrece rechazar y cualquier intento de aprobar se rechaza y queda como `INTENTO_RECHAZADO`. Además, si la lectura con IA falla y el sistema degrada a patrones de texto, el error queda en los **Logs** del servidor (sin ningún valor de clave), porque la pantalla seguía diciendo «Gemini» aunque la IA no estuviera respondiendo. Spec primero; 14 pruebas nuevas y 4 mutaciones detectadas. 205 pruebas. |
| 17 oct | `cd01b5f` | **Diagnóstico de la IA, límite de facturas configurable y aviso aclarado (un solo PR).** (1) **`FACTURAS_MAX`** (EA1.5): el límite de facturas por sala se cambia con una variable de Railway, de 1 a 100; un valor inválido vuelve a 5. (2) El cuadro azul del Panel 1 dice ahora «Datos ficticios, solo para práctica» en lugar de «Demo con datos ficticios», para no confundirlo con el modo demo de la IA. (3) El diagnóstico ya no marca como «parecidas» las claves de otros servicios (`MAPBOX_API_KEY`) y lista `FACTURAS_MAX`. (4) Al fusionar `main` dos veces, los IDs de verificación chocaron (VER-0010 y VER-0012): los de `main` conservan su ID y los de esta rama pasaron a **VER-0013** (diagnóstico) y **VER-0014** (este cambio). Lo siguiente es el cambio original: **Línea de diagnóstico de la IA (EA2b.6 a EA2b.8, ET9).** Con `?diagnostico=1` en el enlace, el Panel 1 muestra por qué está o no activa la IA: qué proveedor se eligió, el motivo del modo demo, si cada clave está «definida», «vacía» o «no definida» (**nunca su valor**), nombres de variables con aspecto de clave mal escrita (por ejemplo `GEMINI_APY_KEY`) y los datos del despliegue que Railway inyecta (entorno, servicio y commit). No depende de ninguna variable de entorno, así que sirve justo cuando una variable no llega. Además, los espacios alrededor de una clave se ignoran. Nació de un caso real: la clave de Gemini estaba puesta en Railway y la app seguía en modo demo. 12 pruebas nuevas (incluida una que garantiza que ningún valor de clave aparece en pantalla). 191 pruebas. |
| 17 oct | `6a620bb` | **Revisión de la documentación.** Se pusieron al día el estado (164 pruebas, PR #7), el mapa del repositorio, el estado del alcance de órdenes de compra, el README (página de reglas) y el índice de specs (12 decisiones). Sin cambios de código. |
| 17 oct | `948f7d7` | **Registro de proveedores (OT1, parte de proveedores).** El equipo entregó un listado de 200 proveedores. `data/importar_compras.py` lo convierte a `data/proveedores.yaml` sin dirección, teléfono ni correo, con una cuenta ficticia (OCD3) y las marcas calculadas: 20 comparten `FALLA-999999-X` y 30 tienen la identificación inválida. Los ID de los proveedores de las órdenes cambiaron: queda como OCD12 (enlazar por nombre). El motor **todavía no usa** este registro (OT2). 12 pruebas nuevas, 164 en total. |
| 17 oct | `2f7c3df` | **Spec de órdenes de compra (alcance nuevo).** El equipo entregó 30 proveedores y 30 órdenes de compra de prueba en Excel (no se suben: el repositorio es público y traen datos de contacto). Spec `ordenes-de-compra`: registro de proveedores con identificación tributaria, registro de órdenes, lectura del número de OC en la factura, revisión nueva del motor (OC inexistente o ajena → senior; ya facturada o más de 10 % → frenar; de 5 % a 10 % → persona), consumo desde el acta, página en el Panel 2 y 8 casos de prueba. Al revisar los archivos se encontraron problemas de datos que quedan como decisiones abiertas (OCD1 a OCD11): moneda «Pesos» sin código, IVA del 16 % para todos los países, sin cuentas bancarias, 6 proveedores con la misma identificación falsa y 10 con el RUC corto. **Sin código todavía.** |
| 17 oct | `f0e1093` | **Documentación al día.** `specs/acta-y-csv/tasks.md` gana una tabla de estado (AT1 a AT10: 6 hechas, 3 parciales, 1 pendiente) y su trazabilidad apunta a las pruebas reales (`tests/test_acta.py` y otras; los archivos que citaba no existían). **P23 cerrado:** las specs vigentes son las del árbol actual (`paneles-y-despliegue` con PP1 a PP8 y PD1; `extraccion-y-agente-de-entrada` con EA1 a EA9), que describen el código que existe; las de otra sesión (`dc04e18`, `8bb35bb`) quedan solo como historial. |
| 17 oct | `00b7d23` | **Página de reglas (PT11, PP8).** El entregable del reto pide una pantalla donde la empresa define sus reglas, y no existía. Spec primero: PP8 (7 criterios), diseño y tarea. Panel 2 › Reglas muestra los parámetros vigentes y el techo duro (no editable), permite editarlos, muestra la vista previa (qué cambia, si afloja o restringe y qué facturas de la sala cambiarían de decisión) y pide motivo. Aflojar exige el rol senior; si lo intenta la persona, queda un `INTENTO_RECHAZADO`. El cambio se guarda como `CAMBIO_REGLA` en el acta de la sala, vale solo hacia adelante y solo en esa sala, y la versión pasa a `v12.s1`. El agente de entrada y los paneles deciden con las reglas de la sala. Cierra T11 y la parte de afloja/restringe y techo de T12. 9 pruebas nuevas, 152 en total, `eval.py` 20/20. |
| 17 oct | `5f764ef` | **P25 cerrado: R2.5 implementado.** Spec primero: `design.md` del motor alineado con el código (ficha con `origen_campos` y `segunda_lectura = no_disponible`; criterio R2.5 explicado campo por campo) y EA3.3 y EA6.4 ajustados. Código: R2.5 (un dato obligatorio que viene solo de una aclaración da `AVISO`, salvo que coincida con el acuerdo o el calendario; número y vencimiento siempre avisan), R2.2 con segunda lectura no disponible (imágenes y textos sin campos comparables) y el agente marca `origen_campos`. 11 pruebas nuevas, 4 violaciones nuevas en Hypothesis y 4 mutaciones del motor detectadas. 143 pruebas, `eval.py` 20/20. Diferencias deliberadas con el diseño de la otra sesión: `orden_en_texto` (agrega un `AVISO`) en lugar de `alerta_inyeccion`, y sin `campos_diferentes` ni `aclaraciones` en la ficha. |
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
| P17 | **Falta probar la lectura con IA sobre un archivo propio.** (El respaldo por patrones ya lee una factura electrónica colombiana: ET10.) En Railway, Gemini ya lee los textos de ejemplo (17 oct, diagnóstico en `?diagnostico=1`). Falta subir un PDF y una foto y revisar la ficha, y probar Claude si se quiere. Los nombres de modelo por defecto no se han fijado con `MODELO_GEMINI` (`gemini-2.5-flash` funcionó; `claude-sonnet-5-5` no se probó) | Quien tenga la clave (ET7) |
| P29 | **Compromiso de la reunión con Blinka sin cumplir:** se dijo que ya se trabajaba en ajustar reglas con lenguaje natural y no existe. Entra en la **fase 1** del roadmap (R7) | El equipo lo construye antes de la entrega |
| P30 | **No se conoce el formato del archivo de salida de Blinka** (columnas, tipo de archivo). Se parte de columnas supuestas (AS-D1) | Preguntarle a Blinka |
| P31 | **Los límites de la demo en USD son un supuesto** (equivalen a los de pesos con 1 USD = 4.000 COP). Falta saber en qué moneda fija Blinka los límites de cada cliente | Preguntarle a Blinka |
| P28 | **Una factura con la ficha inválida solo se puede rechazar:** no hay un botón de «pedir los datos de nuevo» ni un canal para avisar al proveedor; quien la rechaza debe pedirle por fuera que la envíe otra vez. Si muchas facturas propias terminan así, casi seguro la IA no está leyendo (modelo inexistente, cuota o clave): mirar los **Logs** de Railway buscando «La lectura con IA falló». El Panel 1 puede decir «Gemini» aunque la lectura haya degradado a patrones | El equipo, si quiere un flujo de reenvío |
| P27 | **`FACTURAS_MAX` no es un tope de gasto.** Limita las facturas por sala, pero quien abra una sala nueva recibe otras tantas. El freno real es la cuota que se ponga en Google AI Studio o Google Cloud. Al subir el límite para pruebas, cada factura o botón de ejemplo con la IA activa gasta una llamada | Quien administre la clave |
| P26 | **Decisiones de `specs/ordenes-de-compra/requirements.md`.** Antes de cargar las órdenes reales hacen falta OCD1 (moneda), OCD12 (enlazar órdenes por nombre) y **OCD13 (ninguno de los proveedores de las órdenes está en el listado de válidos: hace falta un archivo de órdenes nuevo)**. OCD3, OCD4, OCD5 y OCD11 ya están resueltas | El equipo |
| P15 | **Calibración propia del motor** (D1 a D5 siguen abiertas): zona gris 5 % a 10 %, gasto cuenta solo lo pagado o aprobado, periodo = mes en Bogotá, y los ajustes de «Ajustes al construir». Las 20 facturas de `casos.yaml` se escribieron junto con el motor: **faltan casos trampa de otra mano** para que `eval.py` mida de verdad. R2.5 y R2.2 con segunda lectura no disponible tienen pruebas pero **no un caso en `casos.yaml`** (T3 pide uno por criterio) | D y el equipo |
| P33 | **Las 4 facturas XML de ejemplo del equipo no son colombianas:** tienen estructura de CFDI 4.0 de México (`Comprobante`, `Emisor Rfc`, `RegimenFiscal 601`, IVA del 16 %), no UBL de la DIAN, y no traen fecha, vencimiento, número de orden de compra (solo en el nombre del archivo, que no es confiable), cuenta ni sello fiscal. Todas dicen **MXN**, también las de emisores de Colombia y Perú: con la base en USD (R4) los totales quedan entre 640 y 960 USD si son MXN, o en menos de 5 USD si fueran COP (OCD1). Ninguno de los 4 emisores está en los 156 proveedores válidos (OCD13) y uno usa `FALLA-999999-X`. Hoy `agents/archivo.py` rechaza `.xml`. **El motor no revisa que la moneda de la factura corresponda al país del proveedor**: una factura en MXN de un proveedor colombiano solo se convierte | El equipo: confirmar el formato y la moneda de los XML; decidir si una moneda ajena al país del proveedor escala (spec de R5) |
| P32 | **No se sabe si Railway corre el último `main`.** El despliegue se probó con `014409d`; después entraron los PR #10 a #16, y el #16 cambió los proveedores de los ejemplos. Si Railway no redesplegó, los archivos de muestra del `README.md` no coinciden con los datos desplegados. La red de esta sesión no alcanza el dominio de Railway | Abrir `?diagnostico=1` y comparar el commit; redesplegar desde `main` si hace falta |
| P18 | Las facturas de ejemplo dependen de la **fecha de hoy** (calendario de octubre de 2026, ventana de ±5 días). `FECHA_DEMO=2026-10-17` ya está puesta en Railway; falta confirmar en el tablero que la «normal» termina en `PAGAR` | Confirmar en el Panel 2 |

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
| P6 | **El PDF se genera a mano** desde la página en línea (Chromium, A3 horizontal). Si la página cambia, hay que regenerar y subir el PDF. **Las maquetas muestran los beneficiarios de ejemplo anteriores** (Pixel Norte, Cloudwerk…), que ya no están en los datos: conviene regenerarlas con los proveedores válidos | Quien edite el diseño |
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

En orden. El detalle de cada tarea está en `tasks.md` de cada spec. **Lo que sigue después de la reunión con Blinka está en el roadmap de la sección 8b** (R1 a R14); lo de abajo es el plan anterior.

1. ~~Desplegar en Railway~~ (hecho el 17 oct). Falta abrirlo desde otro computador y reiniciar el servicio para comprobar que el acta persiste.
2. **Subir un PDF y una foto propios en el Panel 1** y revisar la ficha (P17). Confirmar en el tablero las decisiones de los cuatro archivos de muestra (descargados y vueltos a subir).
3. **El equipo resuelve las decisiones abiertas** (P1, P9, P10, P11).
4. **Que otra persona escriba casos trampa nuevos** (P15) y los pase por `eval.py`.
4b. ~~Página de reglas~~ (hecha; ver registro).
4c. ~~Órdenes de compra, versión mínima~~ (hecha con órdenes sintéticas, R3). OT5 hecha (el agente lee la OC y el NIT). Falta: un archivo de órdenes con proveedores válidos (OCD13), OT7 (página de órdenes) y la columna en `facturas.csv`.
5. ~~**Control de las 18:00**~~ (pasa: 20/20, 0 pagos indebidos; repetido a las 19:00). Seguir con la fase 1 del roadmap (sección 8b). El enrutador de canal ya está hecho; con tiempo, la capa 3 (agente de reglas en lenguaje natural, T12 vigencias con conflictos, conciliación y página de resumen). Si los casos trampa no pasan, esas horas se usan para corregir el motor.

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

## 8b. Roadmap (derivado de la reunión con Blinka)

Todos los puntos de mejora que salen de la reunión del 17 oct. Las horas son **estimaciones mías**. Estados: **Pendiente**, **En curso**, **Hecho**. «Spec» dice si ya está escrita (primero la spec, después el código).

### Fase 1 · hasta la entrega (dom 18 oct 2026, 8:00 a. m.)

| # | Mejora | Por qué (qué dijo Blinka) | Spec | Estimado | Estado |
|---|---|---|---|---|---|
| R1 | **Archivo de salida `pagos_aprobados.csv`** con las facturas aprobadas (cuenta del registro, canal, monto, moneda, aprobación automática o manual) y botón en el Panel 2 | Decisión acordada: Blinka paga con ese archivo | `specs/archivo-de-salida/` | 3 h | **Hecho** (columnas supuestas, P30) |
| R2 | **Contar el producto como capa de control de los clientes de Blinka** en el pitch, el guion y la demo (Panel 1 como entrada de demostración) | El usuario es el cliente de Blinka | Docs y guion hechos el 17 oct (`docs/guion-demo.md`) | 0,5 h | **Hecho** (falta ensayarlo) |
| R3 | **Órdenes de compra en el motor**, versión mínima: OT1, OT2, OT3 y OT6 | Validar la factura contra la orden de compra | `specs/ordenes-de-compra/` (9 decisiones abiertas, P26) | 4 h (quedan unas 3 h) | **Hecho con órdenes sintéticas** (OT2, OT3, OT6); las órdenes reales siguen bloqueadas por OCD13 |
| R4 | **Moneda base configurable y demo en USD** (límites, presupuesto y tasas en dólares; COP como una moneda más) | Los clientes operan en dólares | `motor-de-reglas` R5.6 a R5.8 | 1,5 h | **Hecho** |
| R5 | **Leer XML de factura electrónica** sin IA (UBL de la DIAN y, por los ejemplos del equipo, CFDI de México; ver P33), más validar el dígito de verificación del NIT en local | Facturas en XML, PDF o foto; validez fiscal | Falta: cambio en `extraccion-y-agente-de-entrada` | 2 h | Pendiente |
| R6 | **Probar la lectura con IA real** con facturas de distintos formatos (PDF, foto, XML) y fijar el modelo (P17) | Cada proveedor tiene su formato | Ya cubierto por EA2 | 1 h | Pendiente |
| R7 | **Agente de reglas en lenguaje natural:** el usuario escribe el cambio en texto (por ejemplo «sube el límite de autopago a 5.000 USD»), la IA lo traduce a un cambio de reglas, se ve la vista previa (afloja/restringe) y una persona lo confirma. **La IA nunca aplica el cambio** | Compromiso dicho en la reunión (P29) | Falta la spec (primero la spec). Sobre la página de reglas actual; las vigencias con conflictos (T12) pueden quedar para después | 5 h | Pendiente |

### Fase 2 · después de la entrega

| # | Mejora | Por qué | Notas | Estimado | Estado |
|---|---|---|---|---|---|
| R8 | **Contratos:** subir un contrato, extraer cuotas y fechas y proponer un calendario de pagos que una persona confirma | «Subir el contrato con la estructura y cadencia de pagos para agendarlos» | La IA solo propone; el motor y las personas deciden. Parte de la base del calendario de facturas esperadas | 6 h | Pendiente |
| R9 | **Revisión de cumplimiento tipo Sarlaft:** escalar al proveedor sin verificación de cumplimiento (dato marcado «supuesto») | Normas de cumplimiento en Colombia | No se afirma que cumplimos la norma; es una señal de riesgo | 2 h | Pendiente |
| R10 | **Verificación real con la autoridad tributaria** (DIAN, SUNAT) | Facturas electrónicas válidas | Necesita acceso a servicios externos; hoy solo se valida el NIT en local (R5) | 6 h o más | Pendiente |
| R11 | **Presupuesto y análisis por centro de costos y por proveedor** | «Equipo de compras de 10 personas» que analiza proveedores y centros de costos | Hoy el presupuesto es uno por periodo | 4 h | Pendiente |
| R12 | **Integración con ERP y contabilidad** (importar órdenes y proveedores por API; exportar a QuickBooks) | Datos estandarizados en los ERP; clientes con QuickBooks | Hoy solo por archivo | 8 h o más | Pendiente |
| R13 | **Servidor MCP propio** (solo consultas y propuestas, nunca decisiones ni pagos) | Blinka ya conecta GPT por MCP | Abre otra puerta hacia el motor: se hace después del agente de reglas (R7) y con el guardarraíl intacto | 6 h | Pendiente |
| R14 | **Constancia de cada descarga del archivo de salida en el acta** (lote, cantidad, huella del archivo) para no enviar dos veces una factura | AS-D3 de la spec del archivo de salida | Requiere cambiar el esquema del acta | 2 h | Pendiente |

### Fuera de alcance (por decisión de Blinka)

- Mover dinero real o llamar a una cuenta bancaria.
- Criptomonedas como foco del producto (la ruta USDC sigue como sugerencia).

### Preguntas para Blinka

1. ¿Qué **columnas y formato** espera en el archivo de salida? (AS-D1)
2. ¿Cómo se identifica a los **clientes** y su cuenta en Blinka?
3. ¿Qué **moneda** se usa para los límites de aprobación de cada cliente?

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
