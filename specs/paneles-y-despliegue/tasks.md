# Tareas: paneles y despliegue

Estado: **borrador**. Requisitos: `requirements.md` · Diseño: `design.md`. Dueño sugerido: **C** (pantallas).

| # | Tarea | Cubre | Estado |
|---|---|---|---|
| PT1 | Núcleo del acta en SQLite (`acta/`): huella, escribir, verificar, estado, CSV, tablero, salas | AC1 a AC7 | Hecho (versión mínima) |
| PT2 | Semilla de ejemplo con las maquetas (`data/demo_semilla.py`) | PP1.1 | Hecho |
| PT3 | `app/comun.py` y `app/apoyo.py` | PP1, PP3, PP5.1 a PP5.4 | Hecho |
| PT4 | Tablero (cifras, tabla, CSV, aviso de consistencia, refresco) | PP4 | Hecho |
| PT5 | Cola de aprobación con motivo obligatorio y canal | PP5 | Hecho |
| PT6 | Calendario y acta (con verificación de cadena) | PP6 | Hecho |
| PT7 | Panel 1: estado público y facturas de ejemplo | PP2 | Hecho (el agente de entrada se conectó en PT9 y los botones se reemplazaron en PT14) |
| PT8 | Detalle de una factura con ficha y revisiones (en el tablero) | PP6.1 | Hecho |
| PT9 | Conectar con el motor (`registrar_decision`) y el agente de entrada | PP5, PP2 | Hecho |
| PT10 | Despliegue en Railway: `Dockerfile`, `railway.toml`, volumen, variables, `README.md` | PD1 | **Hecho:** desplegado en Railway y probado desde fuera el 17 oct (salud, Gemini, `FECHA_DEMO`). Falta comprobar que el acta sobrevive a un reinicio y que corre el último `main` (P32). PostgreSQL pendiente |
| PT11 | Página de reglas: ver, editar con formulario, vista previa, afloja/restringe y `CAMBIO_REGLA` en el acta | PP8, R9.4 a R9.6 | Hecho |
| PT13 | Página «Órdenes de compra», orden citada en el detalle de la factura y prueba de que el Panel 1 no muestra órdenes | PP9, OC6 | Hecho |
| PT12 | Página de resumen de conciliación (capa 3) | AC8 | Pendiente |
| PT14 | Panel 1: quitar los botones de ejemplo y ofrecer cuatro archivos de muestra descargables | PP2.4, PP2.5, EA8.4 | Hecho |
