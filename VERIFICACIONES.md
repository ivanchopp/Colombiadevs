# Verificaciones

Historial generado por la skill `verificador`. No editar a mano: cada fila viene de `.verificaciones/VER-XXXX.json`.

| ID | Fecha | Veredicto | Cambio | Bloqueantes | Advertencias | Commit | Reemplaza |
|---|---|---|---|---|---|---|---|
| VER-0008 | 2026-10-17 13:29 | APROBADO | Página de reglas (PT11, PP8): ver y editar reglas por sala, vista previa (T11), afloja/restringe y techo duro (T12 parcial), CAMBIO_REGLA en el acta | 0 | 1 | 0d0424a | — |
| VER-0007 | 2026-10-17 13:20 | APROBADO | Cierra P25: implementa R2.5 y R2.2 con segunda lectura no disponible; ficha con origen_campos; spec del motor alineada con el codigo; AVANCES actualizado | 0 | 1 | be99999 | — |
| VER-0006 | 2026-10-17 13:14 | APROBADO | AVANCES.md reescrito tras fusionar el PR #2: sin filas ni pendientes duplicados, estado real, registro con commits, y deriva spec-codigo del motor (P25) | 0 | 1 | 77a8763 | — |
| VER-0005 | 2026-10-17 13:02 | APROBADO | Rama claude/focused-dirac-iurhyp: motor de reglas, acta, agente de entrada (Gemini o Claude), paneles y despliegue en Railway; fusion con main (gana la rama en conflictos) | 0 | 3 | 175774a | — |
| VER-0004 | 2026-10-17 11:29 | APROBADO | Esqueleto del código (engine, acta, agents/entrada, app, tests) | 0 | 0 | 682827e | — |
| VER-0003 | 2026-10-17 11:20 | APROBADO | Specs de paneles-y-despliegue (PD1 a PD12, PT1 a PT14), interfaz pública del agente de entrada, y AVANCES/CLAUDE con la skill verificador | 0 | 1 | 24f1039 | — |
| VER-0002 | 2026-10-17 11:10 | APROBADO | requirements.md D2: aclarar que lo pendiente no cuenta para el presupuesto (R3.6) pero sí para el nivel (R5.2) | 0 | 0 | 0aecd8a | — |
| VER-0001 | 2026-10-17 11:02 | APROBADO | design.md: alinear monto_para_nivel con R5.2 (incluir pendiente) | 0 | 1 | 3d9b7b3 | — |

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
