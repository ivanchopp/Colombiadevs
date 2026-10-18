# Tareas: extracción y agente de entrada

Dueño sugerido: **B** (agentes). Requisitos: `requirements.md` · Diseño: `design.md`.

| # | Tarea | Cubre | Estado |
|---|---|---|---|
| ET1 | `archivo.py`: validación y extracción de texto | EA1 | Hecho |
| ET2 | `segunda_lectura.py` y `seguridad.py` | EA3, EA4 | Hecho |
| ET3 | `lectura_ia.py` con cliente inyectable | EA2 | Hecho (Gemini probado en Railway con los textos de ejemplo) |
| ET4 | `aclaraciones.py` y `estado.py` | EA5, EA7 | Hecho |
| ET5 | `flujo.py` y `ejemplos.py` (modo demo) | EA6, EA8 | Hecho |
| ET6 | Panel 1: chat, subida y ejemplos activos | PP2, EA8.3 | Hecho |
| ET7 | Probar con la clave real (Gemini ahora, Claude después) y ajustar el modelo | EA2 | **Parcial:** `gemini-2.5-flash` funciona en Railway (17 oct). Falta un PDF y una foto propios (P17) y probar Claude |
| ET8 | Proveedor intercambiable: Gemini y Claude | EA2b | Hecho (Gemini probado con clave real; Claude sin probar) |
| ET9 | Línea de diagnóstico del proveedor (`?diagnostico=1`) | EA2b.6 a EA2b.8 | Hecho |
| ET10 | Patrones de respaldo para facturas electrónicas colombianas (TOTAL, Razón social, Nro. Doc., moneda del total en letras) | EA3.4 a EA3.8 | Hecho |
| ET12 | Diagnóstico: última falla de lectura con IA y botón «Probar la conexión» con los modelos disponibles | EA2b.10, EA2b.11 | Hecho |
| ET11 | Factura electrónica en XML (UBL/DIAN) sin IA, segunda lectura por patrones y dígito de verificación del NIT en local | EA10 | Hecho |
| ET13 | XML de otros países de Latinoamérica: tabla `FORMATOS` (CFDI, SRI, CFE, NF-e, DTE, Costa Rica, SIFEN), lectura estructural y segunda lectura por patrones con las mismas rutas, decimales estrictos, codificación declarada y XML desconocido leído como texto y escalado | EA11 | Hecho |
