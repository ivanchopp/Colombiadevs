# Criterios de verificación — colombiadevs

Fuentes de verdad: `specs/README.md` (reglas de trabajo), `specs/*/requirements.md`, `design.md`, `tasks.md`, y los PDFs de `docs/` (diseño general y plan). Si un cambio contradice una fuente, gana la fuente salvo que el cambio también la actualice de forma explícita y justificada.

## 1. Alcance y requisitos
- Cada cambio de código debe poder rastrearse a un criterio (R-número) o a una tarea (T-número). Si no, es alcance nuevo → pedir que se escriba primero en la spec (regla de trabajo 1).
- El motor de reglas decide con campos estructurados, sin IA, sin red, sin ejecutar texto de la factura (R1.6, R2.4). Cualquier cambio que introduzca red/IA/escritura en disco dentro de `evaluar` es bloqueante.
- Lo que está en "Fuera" del alcance de una spec (agente de entrada, acta/CSV, paneles, mover dinero real, fraude/cumplimiento) no debe implementarse en esa spec.
- Cambios de plan: spec primero, código después. Código que adelanta a la spec → bloqueante.

## 2. Convenciones
- Idioma: español en specs y documentación.
- Requisitos en notación EARS (CUANDO/SI … ENTONCES / EL MOTOR DE REGLAS DEBERÁ), numerados R<n>.<m>; no reutilizar ni saltarse números.
- Cada criterio debe tener al menos una prueba automática (R11.1); tasks.md indica qué prueba cierra cada tarea.
- Las specs no repiten el diseño general: lo enlazan.
- Decisiones abiertas (D1…) viven al final de `requirements.md`; al resolverse se borran de ahí y se reflejan en el cuerpo.
- Valores de ejemplo (montos, tasas, costos) marcados «supuesto» y editables en `reglas.yaml`, no incrustados en código.
- Código: dinero con `Decimal`, nunca `float`; esquemas cerrados con Pydantic; función `evaluar(ficha, contexto, reglas)` pura; estructura de carpetas de `design.md`.
- Mantener `specs/README.md` (tabla de estado) coherente con lo que cambió.

## 3. Errores y regresiones
- Referencias cruzadas: R-números, T-números, nombres de archivo y enlaces citados deben existir. Verificar con `grep`.
- Coherencia numérica: los parámetros por defecto de `requirements.md`, `design.md`, `tasks.md`, los ejemplos y los PDFs no deben contradecirse (p. ej. `presupuesto_periodo` 100.000.000, `autopago_max` 3.000.000, `techo_duro_pago` 50.000.000).
- Dependencias de `tasks.md` sin ciclos y consistentes con el diagrama.
- Si existen pruebas, lint o build, ejecutarlos y anotar el resultado exacto. Fallo = bloqueante.
- Cambios en docs/*.pdf: no se pueden diferenciar línea a línea; verificar que el texto de las specs siga coincidiendo con ellos y anotarlo.

## 4. Seguridad y secretos
- Buscar claves, tokens, contraseñas, `.env`, cuentas bancarias o documentos de personas reales en el diff.
- Datos de prueba deben ser ficticios.
- Revisar que ningún cambio permita `PAGAR` sin que todas las revisiones sean `OK` (R1.2), que "ante la duda" siga siendo `ESCALAR` (R1.3), y que los techos duros no se puedan cambiar por chat ni aprobación humana (R8.3, R9.5). Debilitar cualquiera de esos puntos es bloqueante.

## Severidades
- **BLOQUEANTE:** contradice una spec o la regla de oro, rompe algo, expone un secreto, o es alcance sin spec.
- **ADVERTENCIA:** inconsistencia menor o deuda que conviene corregir pronto.
- **NOTA:** observación sin acción obligatoria.
