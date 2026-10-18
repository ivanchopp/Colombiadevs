# Verificaciones

Historial generado por la skill `verificador`. No editar a mano: cada fila viene de `.verificaciones/VER-XXXX.json`.

| ID | Fecha | Veredicto | Cambio | Bloqueantes | Advertencias | Commit | Reemplaza |
|---|---|---|---|---|---|---|---|
| VER-0045 | 2026-10-17 21:08 | APROBADO | R6: diagnóstico ampliado de la IA (última falla de lectura y botón Probar la conexión con los modelos disponibles) tras comprobar en Railway que la IA real no lee; spec EA2b.10, EA2b.11, ET12 | 0 | 1 | bc7547d | — |
| VER-0044 | 2026-10-17 20:56 | APROBADO | Fusión de main (PR #22: R5 XML y R7 reglas en lenguaje natural) en la rama de OT7: conserva ambos cambios de app/apoyo.py y renumera las verificaciones de la rama a VER-0042 y VER-0043 | 0 | 0 | bda2db1 | — |
| VER-0043 | 2026-10-17 20:27 | APROBADO | Fusión de main (06e1178, quita menciones a un cargo de Blinka) en la rama de OT7 antes del PR; la verificación de OT7 pasa de VER-0034 a VER-0035 | 0 | 0 | 95178c6 | — |
| VER-0042 | 2026-10-17 20:23 | APROBADO | OT7: página Órdenes de compra en el Panel 2, orden citada en el detalle de la factura, funciones de apoyo y 12 pruebas; spec PP9 y PT13 | 0 | 0 | 865bed0 | — |
| VER-0041 | 2026-10-17 20:53 | APROBADO | Se quita el nombre de una persona de AVANCES y de la guía en PDF | 0 | 0 | 9698a63 | — |
| VER-0040 | 2026-10-17 20:33 | APROBADO | Fusion de main (R2, R3, OT5, PR 18 y 20) en la rama de R5 y R7: segunda lectura del XML ahora tambien compara orden de compra y NIT, XML lee OrderReference, VER renumerados 0035-0039, AVANCES reconciliado | 0 | 1 | cb5d2cb | — |
| VER-0039 | 2026-10-17 20:25 | APROBADO | R7 version minima sin IA: agente de reglas en lenguaje natural (ART1-ART4): agents/reglas_texto.py, caja de texto en la pagina Reglas que solo rellena el formulario, comprobacion de coherencia, origen y pedido en CAMBIO_REGLA; 55 pruebas | 0 | 1 | a1e21e7 | — |
| VER-0038 | 2026-10-17 20:13 | APROBADO | Spec del agente de reglas: la IA decide la ambiguedad y el codigo solo valida (AR2.4, AR2.7), comprobacion de coherencia por codigo de la propuesta contra el pedido (AR2.8, AR3.5, AR8.5); diseno, tareas y AVANCES; sin codigo | 0 | 1 | f06d5c0 | — |
| VER-0037 | 2026-10-17 20:02 | APROBADO | Spec del agente de reglas en lenguaje natural (R7): requisitos AR1-AR8, diseño, tareas ART1-ART6; AVANCES y specs/README; sin codigo | 0 | 1 | 5632263 | — |
| VER-0036 | 2026-10-17 19:20 | APROBADO | R5: factura electronica en XML (UBL/DIAN) leida sin IA, segunda lectura por patrones, digito de verificacion del NIT en local y CUFE; spec EA10, 29 pruebas, README y AVANCES | 0 | 1 | 446684f | — |
| VER-0035 | 2026-10-17 19:11 | APROBADO | AVANCES.md al dia tras fusionar el PR 14: cabecera main 8510675, hash de R4, no probado (R1 y R4 en navegador y Railway), proximas tareas y fila de registro; sin codigo | 0 | 0 | 8510675 | — |
| VER-0034 | 2026-10-17 20:23 | APROBADO | Se quitan las menciones a un cargo de Blinka (AVANCES, spec archivo-de-salida, historial de verificaciones) | 0 | 0 | 865bed0 | — |
| VER-0033 | 2026-10-17 20:10 | APROBADO | OT5: el agente de entrada lee el número de orden de compra y el NIT (IA, patrones y segunda lectura), 3 muestras con OC, obligación O9 en el calendario y arreglo del monto absurdo (1E100) en el motor | 0 | 1 | 60dbd11 | — |
| VER-0032 | 2026-10-17 20:01 | APROBADO | Fusión de main (PR #18, documentación) en la rama de R2 y R3 antes de abrir el PR: conserva VER-0027 de main y renumera las verificaciones de la rama a VER-0028 a VER-0031 | 0 | 0 | 6ec6a2a | — |
| VER-0031 | 2026-10-17 19:22 | APROBADO | Fusión de main (R1 archivo de salida y R4 moneda base USD, PR #14) en la rama de R2 y R3: calendario de los casos de OC en USD, sin moneda por defecto en OrdenCompra y renumeración de verificaciones a VER-0027 a VER-0029 | 0 | 0 | 1764f22 | — |
| VER-0030 | 2026-10-17 19:15 | APROBADO | Fusión de main (PR #15 a #17: 156 proveedores válidos y revisión de la documentación) en la rama de R2 y R3; reasigna las órdenes sintéticas, casos y pruebas a proveedores válidos y renumera VER-0021/0022 a VER-0024/0025 | 0 | 1 | 9202506 | — |
| VER-0029 | 2026-10-17 18:29 | APROBADO | R3: órdenes de compra en el motor (versión mínima): modelos, carga, revisión OC4, 10 casos, 25 pruebas y documentación | 0 | 1 | ea0e355 | — |
| VER-0028 | 2026-10-17 18:22 | APROBADO | R2: guion de la demo y el pitch (docs/guion-demo.md) y registro en AVANCES.md | 0 | 0 | 3990ea3 | — |
| VER-0027 | 2026-10-17 19:54 | APROBADO | AVANCES al día tras el PR #14 (cabecera, mapa del archivo de salida, commit de R4) y P33 con el análisis de 4 facturas XML de ejemplo; sin código | 0 | 0 | 8510675 | — |
| VER-0026 | 2026-10-17 19:10 | APROBADO | Fusion de main (PR 15, 16, 17) en la rama de R1 y R4: datos de base escalados a USD sobre los 156 proveedores, pruebas ajustadas, VER renumerados a 0024 y 0025, AVANCES reconciliado | 0 | 0 | bfef4f4 | — |
| VER-0025 | 2026-10-17 18:28 | APROBADO | R4: moneda base USD y configurable (R5.6-R5.8): datos a USD con escala uniforme 1 USD = 4000 COP, sin COP fijo en motor ni pantallas, regla R5.7; spec, pruebas y AVANCES | 0 | 1 | 3990ea3 | — |
| VER-0024 | 2026-10-17 18:21 | APROBADO | R1: archivo de salida pagos_aprobados.csv (AS1-AS4): solo facturas PAGADA, cuenta del registro, cadena verificada, boton en la pagina Acta; spec, 17 pruebas, README y AVANCES | 0 | 1 | 3990ea3 | — |
| VER-0023 | 2026-10-17 19:01 | APROBADO | Revisión total de la documentación tras el PR #16: AVANCES, README, specs/README, tareas (ET3, ET7, ET8, PT7, PT10), trazabilidad del motor, OCD3 aplicada y P32 nuevo; sin código | 0 | 1 | 4a08313 | — |
| VER-0022 | 2026-10-17 18:54 | APROBADO | El motor usa los 156 proveedores válidos (OCD4, OT2 parcial, OC1.6): lista permitida desde proveedores.yaml y migración de casos, calendario, muestras, semilla de la demo, README y pruebas | 0 | 1 | f65ca8f | — |
| VER-0021 | 2026-10-17 18:44 | APROBADO | Listado de proveedores válidos: data/proveedores.yaml pasa de 200 a 156 proveedores (sin marcas); OCD5 y OCD11 resueltas, OCD13 nueva; AVANCES y specs al día | 0 | 1 | 3990ea3 | — |
| VER-0020 | 2026-10-17 18:14 | APROBADO | AVANCES y spec del archivo de salida: se quitan las notas de Gemini; el agente de reglas en lenguaje natural pasa a la fase 1 del roadmap (R7) y contratos queda R8 | 0 | 1 | 65fcb0f | — |
| VER-0019 | 2026-10-17 18:10 | APROBADO | Documentacion al dia con la reunion con Blinka: enfoque cliente de Blinka, roadmap R1-R14 por fases, pendientes P29-P31 y spec nueva archivo-de-salida (AS1-AS4); sin codigo | 0 | 1 | 07b4849 | — |
| VER-0018 | 2026-10-17 17:08 | APROBADO | Panel 1 sin botones de ejemplo: solo se sube archivo, 4 archivos de muestra descargables con rotulos neutros (PP2.4, PP2.5, EA8.4); spec, pruebas, README y AVANCES | 0 | 1 | bb0f497 | — |
| VER-0017 | 2026-10-17 16:37 | APROBADO | Patrones de respaldo para facturas electronicas colombianas (EA3.4 a EA3.8): TOTAL, Razon social, Nro. Doc., moneda del total en letras; spec, pruebas y AVANCES | 0 | 1 | 6d2d137 | — |
| VER-0016 | 2026-10-17 16:23 | APROBADO | AVANCES.md: se registra el despliegue en Railway probado (salud, Gemini activo, FECHA_DEMO), se cierra P20, se acotan P17 y P18 y se actualizan próximas tareas | 0 | 1 | 014409d | — |
| VER-0015 | 2026-10-17 16:11 | APROBADO | Arreglo: una factura con ficha invalida se registra escalada (R8.6) y aparece en el tablero; no se puede aprobar (PP5.7); errores de lectura con IA en los Logs sin claves (EA2b.9); specs y AVANCES | 0 | 2 | 014409d | — |
| VER-0014 | 2026-10-17 16:02 | APROBADO | FACTURAS_MAX configurable (EA1.5), aviso del Panel 1 sin la palabra demo, diagnostico sin falsos positivos de otros servicios, y fusion de main con renumeracion de VER-0010 a VER-0012; specs y AVANCES al dia | 0 | 1 | 5fba303 | — |
| VER-0013 | 2026-10-17 14:02 | APROBADO | Linea de diagnostico de la IA en el Panel 1 (?diagnostico=1): proveedor, motivo del modo demo, estado de cada variable sin mostrar valores, nombres parecidos y datos del despliegue; espacios en claves ignorados; spec EA2b.6-8 y AVANCES | 0 | 1 | 67eb333 | — |
| VER-0012 | 2026-10-17 16:00 | APROBADO | Revisión de la documentación: estado (164 pruebas, PR #7), mapa del repositorio, alcance de órdenes de compra, README (página de reglas) e índice de specs | 0 | 0 | 7527f07 | — |
| VER-0011 | 2026-10-17 15:40 | APROBADO | Registro de proveedores (OT1, parte de proveedores): importar_compras.py, data/proveedores.yaml con 200 proveedores y pruebas; spec con OCD12 | 0 | 2 | 2f7c3df | — |
| VER-0010 | 2026-10-17 14:24 | APROBADO | Spec nueva ordenes-de-compra (OC1 a OC8, diseño, OT1 a OT7, decisiones OCD1 a OCD11) y enlaces en specs/README, motor-de-reglas y AVANCES | 0 | 1 | 67eb333 | — |
| VER-0009 | 2026-10-17 13:54 | APROBADO | Documentación: estado de AT1 a AT10 en specs/acta-y-csv/tasks.md, trazabilidad apuntando a las pruebas reales y P23 cerrado en AVANCES.md | 0 | 0 | b6e1beb | — |
| VER-0008 | 2026-10-17 13:29 | APROBADO | Página de reglas (PT11, PP8): ver y editar reglas por sala, vista previa (T11), afloja/restringe y techo duro (T12 parcial), CAMBIO_REGLA en el acta | 0 | 1 | 0d0424a | — |
| VER-0007 | 2026-10-17 13:20 | APROBADO | Cierra P25: implementa R2.5 y R2.2 con segunda lectura no disponible; ficha con origen_campos; spec del motor alineada con el codigo; AVANCES actualizado | 0 | 1 | be99999 | — |
| VER-0006 | 2026-10-17 13:14 | APROBADO | AVANCES.md reescrito tras fusionar el PR #2: sin filas ni pendientes duplicados, estado real, registro con commits, y deriva spec-codigo del motor (P25) | 0 | 1 | 77a8763 | — |
| VER-0005 | 2026-10-17 13:02 | APROBADO | Rama claude/focused-dirac-iurhyp: motor de reglas, acta, agente de entrada (Gemini o Claude), paneles y despliegue en Railway; fusion con main (gana la rama en conflictos) | 0 | 3 | 175774a | — |
| VER-0004 | 2026-10-17 11:29 | APROBADO | Esqueleto del código (engine, acta, agents/entrada, app, tests) | 0 | 0 | 682827e | — |
| VER-0003 | 2026-10-17 11:20 | APROBADO | Specs de paneles-y-despliegue (PD1 a PD12, PT1 a PT14), interfaz pública del agente de entrada, y AVANCES/CLAUDE con la skill verificador | 0 | 1 | 24f1039 | — |
| VER-0002 | 2026-10-17 11:10 | APROBADO | requirements.md D2: aclarar que lo pendiente no cuenta para el presupuesto (R3.6) pero sí para el nivel (R5.2) | 0 | 0 | 0aecd8a | — |
| VER-0001 | 2026-10-17 11:02 | APROBADO | design.md: alinear monto_para_nivel con R5.2 (incluir pendiente) | 0 | 1 | 3d9b7b3 | — |

## VER-0045 — APROBADO

- **ADVERTENCIA** (alcance) `app/Panel_1_Proveedor.py:25`: El botón de prueba lo puede pulsar quien tenga el enlace con ?diagnostico=1 y gasta una llamada a la IA cada vez (una lectura mínima y un listado de modelos); es una demo con datos ficticios y el parámetro no está enlazado desde ningún lado → Si preocupa el gasto, limitar la cuota en Google AI Studio (P27)
- **NOTA** (errores) `AVANCES.md:19`: Se corrige una afirmación anterior: las lecturas «con IA real» de los botones de muestra eran lecturas guardadas (LECTURAS_GUARDADAS); la IA real nunca se había probado en producción hasta R6 → Ninguna

## VER-0044 — APROBADO

- **NOTA** (convenciones) `.verificaciones/VER-0042.json:2`: Los IDs VER-0035 y VER-0036 los ocuparon verificaciones de R5 y R7 en main; se conservaron los de main y las de OT7 pasaron a VER-0042 y VER-0043 → Ninguna

## VER-0043 — APROBADO

- **NOTA** (convenciones) `.verificaciones/VER-0035.json:2`: El ID VER-0034 lo ocupó otra sesión en main; se conservó el de main y la verificación de OT7 se renumeró a VER-0035 → Ninguna

## VER-0042 — APROBADO

- **NOTA** (convenciones) `app/pages/6_Ordenes_de_compra.py:1`: El menú lateral de Streamlit muestra «Ordenes de compra» sin tilde (sale del nombre del archivo), igual que P12 → Opcional: st.navigation
- **NOTA** (alcance) `data/ordenes_compra.yaml:1`: La página muestra las órdenes sintéticas (OCD13) y lo dice en pantalla («de ejemplo, supuesto»); falta la columna orden_compra en facturas.csv → Hacerlo cuando lleguen las órdenes reales

## VER-0040 — APROBADO

- **ADVERTENCIA** (alcance) `agents/xml_factura.py`: El lector de XML solo entiende UBL (DIAN y otros paises); los 4 XML de ejemplo del equipo son CFDI 4.0 de Mexico y se rechazan con No es una factura UBL (AVANCES P33) → Decidir si se agrega el CFDI
- **NOTA** (errores) `agents/segunda_lectura.py`: Main agrego que la orden de compra y el NIT cuenten en la segunda lectura; el XML ahora los lee con ambos metodos para que coincidan, y flujo.py no pisa el NIT que ya leyo la IA o los patrones

## VER-0039 — APROBADO

- **ADVERTENCIA** (alcance) `agents/reglas_texto.py`: Solo el lector por patrones: entiende frases simples y todo lo demas es no entendido. La IA (ART5), el tope por sala, la degradacion y el cliente falso de IA no estan; el vocabulario fijo de la comprobacion de coherencia puede dar falsas alarmas → Hacer ART5 y calibrar con pedidos reales
- **NOTA** (seguridad) `app/pages/5_Reglas.py`: El texto no tiene camino propio hacia las reglas: solo rellena el formulario, y validar_cambio, el techo duro, la firma del senior, el motivo y el acta son los de siempre; una propuesta dudosa exige la marca de revision; si la persona edita la cifra despues, el origen vuelve a formulario

## VER-0038 — APROBADO

- **ADVERTENCIA** (alcance) `specs/agente-de-reglas/requirements.md`: La comprobacion de coherencia (AR2.8) usa un vocabulario fijo y una lectura de numeros por codigo: puede dar falsas alarmas o dejar pasar un caso raro; por eso solo marca como dudosa y exige una marca de revision, no rechaza → Calibrar con la tabla de pedidos de AR8.5 al programarla

## VER-0037 — APROBADO

- **ADVERTENCIA** (alcance) `specs/agente-de-reglas/requirements.md`: Seis decisiones abiertas (AR-D1 a AR-D6) con propuesta por defecto; el agente no esta programado y se calcula en unas 7 horas (4,5 h la version minima sin IA) → El equipo confirma las decisiones antes de programar
- **NOTA** (seguridad) `specs/agente-de-reglas/design.md`: El agente no tiene camino propio hacia las reglas: solo rellena el formulario existente, asi que validar_cambio, el techo duro, la firma del senior y el motivo se cumplen por construccion; la IA no recibe valores vigentes ni datos de la empresa

## VER-0036 — APROBADO

- **ADVERTENCIA** (alcance) `agents/id_tributaria.py`: El digito de verificacion solo prueba que el NIT esta bien formado; no consulta a la DIAN ni prueba que la factura sea valida (R10). El XML de prueba es ficticio y no se probo con un XML real de la DIAN → Probar con un XML real y planear R10
- **NOTA** (errores) `agents/flujo.py`: Una factura con NIT dudoso o sin CUFE queda escalada sin que finanzas vea el motivo en pantalla (la ficha es cerrada); el motivo solo sale en los Logs → Mostrar el motivo cuando entre el NIT a la ficha (R3)
- **NOTA** (seguridad) `agents/xml_factura.py`: Se rechaza todo XML con DOCTYPE o ENTITY antes de analizarlo, y un XML nunca usa la IA; ninguna senal nueva afloja una regla, solo puede volver la lectura dudosa

## VER-0035 — APROBADO

- **NOTA** (convenciones) `AVANCES.md`: La hora de la ultima actualizacion sale del reloj de la sesion (19:15 Bogota); las horas de filas anteriores del registro fueron aproximadas → Ninguna

## VER-0033 — APROBADO

- **ADVERTENCIA** (alcance) `specs/ordenes-de-compra/design.md`: La spec de OT5 se escribió después del código en la misma sesión (la regla pide spec primero); el contenido describe lo construido y las pruebas lo cubren → Escribir la spec antes en los próximos cambios
- **NOTA** (errores) `engine/evaluar.py:88`: Se corrigió de paso un fallo previo de main: un monto absurdo (1E100) lanzaba InvalidOperation en el motor; ahora escala (R1.3). Lo encontró la prueba de propiedades → Ninguna
- **NOTA** (alcance) `data/ordenes_compra.yaml:1`: Las órdenes siguen siendo sintéticas (OCD13); el agente no pregunta por la OC en el chat, así que OC3.4 no se produce → Importar las órdenes reales cuando existan

## VER-0032 — APROBADO

- **NOTA** (convenciones) `AVANCES.md:17`: Las cifras de 266 pruebas y 29 casos valen en la rama; en main son 240 y 20 hasta que se fusione el PR → Actualizar al fusionar

## VER-0031 — APROBADO

- **NOTA** (convenciones) `AVANCES.md:5`: En main siguen 240 pruebas y 20 casos; las cifras de 266 y 29 valen solo en la rama hasta que se fusione (AVANCES lo dice) → Actualizar al fusionar el PR
- **NOTA** (errores) `data/casos.yaml:1`: Los casos de OC usan calendario_extra en USD (COP × 0,00025); si cambia la tasa del peso en tasas.yaml hay que recalcularlos → Ninguna ahora

## VER-0030 — APROBADO

- **ADVERTENCIA** (alcance) `data/ordenes_compra.yaml:1`: Las órdenes siguen siendo sintéticas: el archivo real no tiene proveedores del listado de válidos (OCD13) y no está cargado → Conseguir un archivo de órdenes con proveedores válidos e importarlo (OT1)
- **NOTA** (errores) `tests/test_ordenes_compra.py:1`: El listado de válidos no trae proveedores marcados: OC4.4 se prueba marcando uno a mano, no con un dato real → Ninguna mientras el listado no traiga marcas
- **NOTA** (convenciones) `.verificaciones/VER-0024.json:2`: Los IDs VER-0021 y VER-0022 de esta rama chocaron con los de main y se renumeraron a VER-0024 y VER-0025; el contenido y la fecha originales se conservan → Ninguna

## VER-0029 — APROBADO

- **ADVERTENCIA** (alcance) `data/ordenes_compra.yaml:1`: Las órdenes son sintéticas: el archivo real del equipo no está en el repositorio. La spec y AVANCES lo declaran; los resultados con las órdenes reales pueden diferir → Importar el .xlsx real (OT1) y volver a correr eval.py
- **NOTA** (alcance) `engine/revisiones/orden_compra.py:1`: El agente de entrada aún no lee el número de OC (OT5): una factura subida al Panel 1 no cita OC, por lo que la revisión nueva solo actúa con fichas de prueba → Hacer OT5
- **NOTA** (seguridad) `engine/reglas_io.py:50`: Los 200 proveedores pasan a la lista permitida sin acuerdo: sin OC ni acuerdo siguen escalando a PERSONA (R3.5) y los marcados van al senior; ningún camino nuevo paga sin todas las revisiones OK (R1.2) → Ninguna

## VER-0028 — APROBADO

- **NOTA** (alcance) `docs/guion-demo.md:36`: Los resultados de cada archivo de muestra no se verificaron uno por uno en producción; el guion lo declara y pide confirmarlos en el ensayo → Ensayar el guion en la app desplegada

## VER-0027 — APROBADO

- **NOTA** (alcance) `AVANCES.md`: Las 4 facturas XML no se suben: el repositorio es público y vienen de fuera; P33 solo describe lo encontrado → Ninguna

## VER-0026 — APROBADO

- **NOTA** (errores) `data/calendario.csv`: Con los 156 proveedores, la obligacion O4 (2.850.350 COP) no es multiplo exacto de la tasa 1/4000 y se redondeo a 712,59 USD; el emparejamiento por tolerancia no cambia → Ninguna

## VER-0025 — APROBADO

- **ADVERTENCIA** (alcance) `data/reglas.yaml`: Los limites en USD son un supuesto (equivalen a los de pesos con 1 USD = 4000 COP); no se sabe en que moneda fija Blinka los limites de cada cliente (AVANCES P31) → Preguntarle a Blinka
- **NOTA** (errores) `data/tasas.yaml`: Con la base en USD el redondeo es a centavos de USD: una diferencia de 1 COP en el limite del 10 por ciento ya no se distingue; la prueba de zona gris usa 400 COP de margen → Documentado en el diseno del motor
- **NOTA** (seguridad) `engine/revisiones/montos.py`: R5.7 escala al senior si la tabla de cambio no da 1 para la base; ninguna regla se afloja y las 20 decisiones de prueba no cambian → Ninguna

## VER-0024 — APROBADO

- **ADVERTENCIA** (alcance) `acta/exportar_pagos.py`: Las columnas del archivo son un supuesto: no se conoce el formato que espera Blinka (AS-D1, AVANCES P30). id_tributaria y orden_compra salen vacias hasta que entren las ordenes de compra (R3) → Confirmar el formato con Blinka
- **NOTA** (seguridad) `acta/exportar_pagos.py`: Una aprobada manualmente cuyo beneficiario no esta en el registro (por ejemplo un beneficiario nuevo aprobado por el senior) no entra al archivo y se avisa; es la decision AS-D2 por omision → Decidir si se actualiza el registro de proveedores al aprobar
- **NOTA** (errores) `app/pages/4_Acta.py`: El archivo se genera en cada recarga de la pagina y el lote_id lleva la hora; dos descargas seguidas tienen lotes distintos y nada impide enviar dos veces la misma factura (R14, AS-D3) → Constancia en el acta en una segunda etapa

## VER-0023 — APROBADO

- **ADVERTENCIA** (errores) `specs/motor-de-reglas/tasks.md`: Los 'Listo cuando' de T4 a T8 siguen nombrando archivos de prueba que no existen (test_entrada.py, test_decision.py...); la tabla de trazabilidad ya apunta a tests/test_motor.py y lo aclara → Dejarlo así (registro histórico) o reescribir esas líneas si se retoma la spec
- **NOTA** (alcance) `docs/Ruta-de-una-factura.pdf`: Las maquetas del PDF siguen con los beneficiarios anteriores (P6); no se pueden regenerar desde aquí → Regenerar desde la página en línea del equipo
- **NOTA** (errores) `AVANCES.md`: No se pudo comprobar qué commit corre Railway: la red de la sesión no alcanza el dominio (403 del proxy) → Revisar ?diagnostico=1 (P32)

## VER-0022 — APROBADO

- **ADVERTENCIA** (alcance) `docs/Ruta-de-una-factura.pdf`: Las maquetas del PDF muestran los beneficiarios de ejemplo anteriores → Regenerar el PDF (P6)
- **NOTA** (alcance) `data/demo_semilla.py`: Brasil y Alemania no están en el listado de válidos: sus papeles pasaron a Perú (montos convertidos de BRL a PEN) y Ecuador (USD); el canal sugerido cambia de Pix y SEPA a transferencia en Perú y SWIFT → Ninguna
- **NOTA** (seguridad) `engine/reglas_io.py:registros_de_proveedores`: Un acuerdo o un movimiento de un proveedor que no está en el registro hace fallar la carga en vez de quedar como beneficiario permitido → Ninguna

## VER-0021 — APROBADO

- **ADVERTENCIA** (alcance) `specs/ordenes-de-compra/requirements.md:OCD13`: Ninguno de los 30 proveedores de las órdenes de compra está en el listado de válidos; sus órdenes no se pueden cargar sin escalar todas → Pedir un archivo de órdenes con proveedores válidos
- **NOTA** (alcance) `data/registros.yaml`: No se tocan los 9 beneficiarios con los que decide el motor: eliminarlos rompería los 20 casos, el calendario y la demo; reemplazarlos es OCD4 y OT2 → Decidir OCD4

## VER-0020 — APROBADO

- **ADVERTENCIA** (alcance) `AVANCES.md`: El agente de reglas en lenguaje natural entra en la fase 1 sin spec escrita; hay que escribirla antes de programar (primero la spec) → Escribir la spec del agente de reglas antes de R7

## VER-0019 — APROBADO

- **ADVERTENCIA** (alcance) `specs/archivo-de-salida/requirements.md`: El formato real del archivo que espera Blinka no se conoce; las columnas son un supuesto marcado y hay 4 decisiones abiertas (AS-D1 a AS-D4) → Preguntarle a Blinka antes de programar AST1
- **NOTA** (convenciones) `AVANCES.md`: Las horas del roadmap son estimaciones y las notas de la reunion son de Gemini con errores de transcripcion; solo se uso lo claro → Confirmar con el equipo

## VER-0018 — APROBADO

- **ADVERTENCIA** (alcance) `app/Panel_1_Proveedor.py`: Sin IA los archivos de muestra se leen con patrones y siempre se escalan (EA8.2): el caso normal solo llega a PAGAR con la IA activa, y esa lectura real no esta probada (AVANCES P17) → Probar los 4 archivos en Railway con Gemini activo
- **NOTA** (seguridad) `app/Panel_1_Proveedor.py`: Ningun camino de la app usa ya las lecturas guardadas; los rotulos de descarga no revelan el caso ni la regla (PP2.1) → Ninguna

## VER-0017 — APROBADO

- **ADVERTENCIA** (alcance) `agents/segunda_lectura.py`: Los patrones se probaron con un solo formato real de factura electronica; otros formatos pueden seguir sin leerse. No se probo la lectura con Gemini sobre ese PDF (AVANCES P17) → Probar el PDF en Railway con la IA activa
- **NOTA** (seguridad) `agents/segunda_lectura.py`: Una lectura por patrones sigue marcada dudosa (EA8.2) y la segunda lectura exige coincidencia con la IA: ninguna ampliacion puede llevar a PAGAR por si sola → Ninguna

## VER-0016 — APROBADO

- **ADVERTENCIA** (convenciones) `AVANCES.md:14`: La sección 1 dice que la última verificación es VER-0011, pero ya existen VER-0013 y VER-0014 (deuda previa, no de este cambio) → Actualizar la cifra al registrar la siguiente verificación
- **NOTA** (errores) `AVANCES.md:6`: La línea del repositorio sigue diciendo PR #7 como último; ya entró el PR #9 (deuda previa) → Actualizar en la próxima revisión de documentación

## VER-0015 — APROBADO

- **ADVERTENCIA** (alcance) `app/pages/2_Cola_de_aprobacion.py`: Una ficha invalida solo se puede rechazar: no hay boton ni canal para pedir al proveedor que reenvie los datos; quien rechaza debe avisarle por fuera → Decidir si se construye un flujo de reenvio (AVANCES P28)
- **ADVERTENCIA** (errores) `agents/flujo.py`: El Panel 1 puede decir Gemini aunque la lectura haya degradado a patrones de texto por un fallo de la API; el unico rastro esta en los Logs del servidor → Revisar los Logs de Railway buscando La lectura con IA fallo (AVANCES P28)
- **NOTA** (seguridad) `engine/guardarrail.py`: Una ficha invalida nunca llega a PAGAR: se registra ESCALAR/SENIOR, la aprobacion se rechaza en el guardarrail y la cola no ofrece el boton; proponer PAGAR con ficha invalida se rechaza y deja INTENTO_RECHAZADO. No cambia ninguna regla de decision para fichas validas → Ninguna

## VER-0014 — APROBADO

- **ADVERTENCIA** (seguridad) `agents/flujo.py`: FACTURAS_MAX no es un tope de gasto: limita las facturas por sala, pero cada sala nueva recibe otras tantas, y subirlo aumenta las llamadas reales a la IA → Poner una cuota en Google AI Studio o Google Cloud (AVANCES P27)
- **NOTA** (errores) `.verificaciones/VER-0010.json`: La fusion con main encontro dos VER-0010 distintos; el de main conserva su ID y el de esta rama se renumero a VER-0012 antes de llegar a main; la tabla se regenero con el script del verificador → Ninguna
- **NOTA** (convenciones) `agents/lectura_ia.py`: El diagnostico ya no detecta nombres parecidos de claves genericas (API_KEY) ni de otros servicios; solo Gemini, Google y Anthropic → Ampliar PARECE_DE_IA si hace falta

## VER-0013 — APROBADO

- **ADVERTENCIA** (seguridad) `app/Panel_1_Proveedor.py`: El diagnostico es publico (Panel 1 es abierto) y revela cuales variables de IA estan definidas, el entorno, el servicio y 7 caracteres del commit; no muestra ningun valor de clave. Es informacion de baja sensibilidad pero conviene saberlo → Si se quiere restringir, exigir una clave de demostracion o quitar el parametro antes de la entrega
- **NOTA** (errores) `agents/lectura_ia.py`: La deteccion de nombres parecidos es heuristica (regex) y puede no marcar un error de escritura raro o marcar una variable legitima inesperada → Ajustar PARECE_DE_IA si aparece un falso positivo

## VER-0012 — APROBADO

- **NOTA** (errores) `AVANCES.md`: Se corrigieron datos desactualizados: 152 y 143 pruebas (son 164), repositorio en PR #2 (va en PR #7), un commit sin número y el estado del alcance de órdenes de compra → Ninguna

## VER-0011 — APROBADO

- **ADVERTENCIA** (alcance) `data/proveedores.yaml`: El motor todavía no usa este registro: R4.1 sigue leyendo los 9 beneficiarios de registros.yaml, así que ningún proveedor nuevo se paga solo hasta OT2 → Implementar OT2 tras resolver OCD4
- **ADVERTENCIA** (errores) `specs/ordenes-de-compra/requirements.md:OCD12`: Los ID de proveedor del archivo de órdenes ya no coinciden con el listado de 200 → Enlazar por nombre al importar las órdenes
- **NOTA** (seguridad) `data/proveedores.yaml`: Sin dirección, teléfono ni correo (prueba automática); el .xlsx no se sube; cuentas ficticias marcadas → Ninguna

## VER-0010 — APROBADO

- **ADVERTENCIA** (alcance) `specs/ordenes-de-compra/requirements.md:Decisiones abiertas`: Los datos entregados tienen inconsistencias (moneda sin código, IVA 16 % para todos, sin cuentas, 16 de 30 identificaciones repetidas o con formato inválido) que cambian los resultados esperados → Resolver OCD1, OCD3, OCD4, OCD5 y OCD11 antes de OT1
- **NOTA** (seguridad) `data/fuentes`: Los Excel originales no se suben: el repositorio es público y traen dirección, teléfono y correo; OC1.2 lo deja escrito → Ninguna
- **NOTA** (alcance) `specs/ordenes-de-compra/tasks.md`: Unas 7 h de trabajo frente a la entrega de las 8:00; hay versión mínima de unas 4 h → El equipo decide si entra

## VER-0009 — APROBADO

- **NOTA** (errores) `specs/acta-y-csv/tasks.md:Trazabilidad`: AC7.3, AC7.4, AC8 y AC9.9 quedan sin prueba porque no están implementados; se dejó explícito en la tabla → Agregar pruebas si se implementan

## VER-0008 — APROBADO

- **ADVERTENCIA** (alcance) `app/apoyo.py:cambiar_reglas`: Quien pide y quien firma un cambio que afloja es el mismo rol de demostración: no hay separación de funciones real entre solicitante y firmante (R8.2 la exige para aprobaciones, R9.4 solo pide la firma del senior) → Si se quiere, exigir que el senior firme un cambio pedido por otra persona en un segundo paso
- **NOTA** (alcance) `engine/reglas_io.py:reglas_de_sala`: El cambio se aplica desde que se confirma, no según la fecha de recepción de la factura (R9.2); es lo esperado para la demo y está documentado como shortcut en design.md → Revisar si se implementan vigencias con conflictos (T12)
- **NOTA** (seguridad) `engine/reglas_io.py:validar_cambio`: El senior puede subir tolerancia_frenar hasta 100 %; lo permite la spec. Los umbrales de monto siguen acotados por el techo duro y R8.3 no cambia → Ninguna

## VER-0007 — APROBADO

- **ADVERTENCIA** (alcance) `data/casos.yaml`: R2.5 y R2.2 con segunda lectura no disponible tienen pruebas unitarias y de propiedades pero no un caso en casos.yaml (T3 pide un caso por criterio de R2 a R5); anadirlos cambiaria el total de 20 casos → Decidir si se amplia el set de casos (AVANCES P15)
- **NOTA** (convenciones) `specs/motor-de-reglas/design.md`: La ficha difiere deliberadamente del diseno de otra sesion: orden_en_texto en lugar de alerta_inyeccion y sin campos_diferentes ni aclaraciones; documentado en Ajustes al construir → Confirmar con el equipo (P23)
- **NOTA** (seguridad) `engine/revisiones/entrada.py`: R2.5 solo agrega cautela: un dato aclarado que coincide con registros no avisa, pero R2.2, R4 y las demas revisiones siguen aplicando y segunda_lectura no puede cambiarse por chat → Ninguna

## VER-0006 — APROBADO

- **ADVERTENCIA** (errores) `specs/motor-de-reglas/requirements.md:80`: El criterio R2.5 y los campos de ficha del diseno (origen_campos, no_disponible, campos_diferentes, alerta_inyeccion, aclaraciones) no estan implementados y R2.5 no tiene prueba; design.md se contradice con su seccion Ajustes al construir. VER-0005 no lo detecto → Implementar R2.5 con prueba o reescribir el criterio y la ficha (AVANCES P25)
- **NOTA** (convenciones) `AVANCES.md`: Se quitaron las decisiones EXD y PDD que apuntaban a specs sustituidas y se reemplazaron por DE1-DE4 y DP1-DP2 → Ninguna

## VER-0005 — APROBADO

- **ADVERTENCIA** (alcance) `specs/paneles-y-despliegue y specs/extraccion-y-agente-de-entrada`: En la fusion se sustituyeron por las de esta rama las specs que otra sesion subio a main (PD1-PD12, PT1-PT14, interfaz publica del agente de entrada); siguen en el historial → El equipo debe confirmar que specs valen (AVANCES P23)
- **ADVERTENCIA** (errores) `agents/lectura_ia.py`: La lectura con IA real (Gemini y Claude) y la imagen de Docker/Railway no se han probado: solo clientes falsos y construccion de los clientes de los SDK sin red → Correr python3 -m agents.probar con una clave y desplegar en Railway
- **ADVERTENCIA** (convenciones) `specs/extraccion-y-agente-de-entrada/requirements.md`: Numeracion EA2b no consecutiva (la regla pide no saltarse ni reutilizar numeros) → Renumerar si el equipo lo exige
- **NOTA** (alcance) `acta/esquema_postgres.sql`: Esquema PostgreSQL de main conservado pero sin conectar ni probar; el almacen es solo SQLite → Pendiente P13
- **NOTA** (errores) `historial de la rama`: Los commits previos no pasaron por el verificador porque la regla llego a main despues; se verifica la rama completa → Ninguna

## VER-0004 — APROBADO

- **NOTA** (alcance) `acta/esquema_postgres.sql`: Esquema PostgreSQL y despliegue en Railway sin probar → Probar en PT1
- **NOTA** (errores) `engine/evaluar.py`: Una revisión OK con nivel exigido no escalaba; corregido y con prueba

## VER-0003 — APROBADO

- **ADVERTENCIA** (errores) `specs/paneles-y-despliegue/design.md`: Los nombres de opciones de Streamlit y Railway (run_every, query_params, healthcheckPath, startCommand) no se pudieron comprobar contra la documentación desde este entorno → Confirmarlos en la documentación y la versión instalada antes de fijarlos; la spec ya lo indica
- **NOTA** (convenciones) `specs/paneles-y-despliegue/requirements.md`: Los valores de la tabla de parámetros son de demostración y están marcados así → Ninguna

## VER-0001 — APROBADO

- **ADVERTENCIA** (convenciones) `specs/motor-de-reglas/requirements.md:158`: D2 dice que lo pendiente no cuenta para el presupuesto, mientras R5.2 sí lo cuenta para el nivel; la diferencia es intencional pero no está escrita → aclarar en D2 que aplica solo a R3.6 (presupuesto), no a R5.2
