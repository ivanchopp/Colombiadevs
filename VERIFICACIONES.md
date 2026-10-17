# Verificaciones

Historial generado por la skill `verificador`. No editar a mano: cada fila viene de `.verificaciones/VER-XXXX.json`.

| ID | Fecha | Veredicto | Cambio | Bloqueantes | Advertencias | Commit | Reemplaza |
|---|---|---|---|---|---|---|---|
| VER-0012 | 2026-10-17 14:02 | APROBADO | Linea de diagnostico de la IA en el Panel 1 (?diagnostico=1): proveedor, motivo del modo demo, estado de cada variable sin mostrar valores, nombres parecidos y datos del despliegue; espacios en claves ignorados; spec EA2b.6-8 y AVANCES | 0 | 1 | 67eb333 | — |
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

## VER-0012 — APROBADO

- **ADVERTENCIA** (seguridad) `app/Panel_1_Proveedor.py`: El diagnostico es publico (Panel 1 es abierto) y revela cuales variables de IA estan definidas, el entorno, el servicio y 7 caracteres del commit; no muestra ningun valor de clave. Es informacion de baja sensibilidad pero conviene saberlo → Si se quiere restringir, exigir una clave de demostracion o quitar el parametro antes de la entrega
- **NOTA** (errores) `agents/lectura_ia.py`: La deteccion de nombres parecidos es heuristica (regex) y puede no marcar un error de escritura raro o marcar una variable legitima inesperada → Ajustar PARECE_DE_IA si aparece un falso positivo

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
