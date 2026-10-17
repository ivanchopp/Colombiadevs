# Requisitos: base de proveedores y prioridad

Estado: **borrador para revisión del equipo**.
Amplía `specs/motor-de-reglas/`. Reemplaza las listas sueltas de beneficiarios, cuentas y acuerdos de `registros.yaml` por una tabla de proveedores.

## Resumen

La empresa mantiene una **base de proveedores**: quién es, a qué cuenta se le paga, qué se acordó con él y qué tan importante es pagarle a tiempo. El motor la lee para decidir (R4) y la cola de aprobación la usa para ordenar.

**Regla central: la prioridad ordena, no relaja.** La prioridad define quién se atiende o se paga primero. **Nunca cambia umbrales, niveles ni reglas.** Un proveedor «prioritario» pasa por exactamente los mismos controles que cualquier otro.

## Glosario

| Término | Significado |
|---|---|
| Proveedor | Beneficiario registrado de la empresa. |
| `estado` | `NUEVO`, `ACTIVO` o `BLOQUEADO`. |
| `prioridad` | `A`, `B` o `C`. A es la más urgente. Solo ordena. |
| Cuenta registrada | Cuenta de pago verificada por la empresa. |
| Maestro de proveedores | La tabla `proveedores`. En el reto es de demostración y hace de ERP. |

## Campos de la tabla

| Campo | Ejemplo | Nota |
|---|---|---|
| `id` | `PRV-001` | Único |
| `nombre` | «Papelería Andina S. A. S.» | Ficticio |
| `documento_tributario` | `900.000.001-1` | Ficticio, marcado «supuesto» |
| `pais` / `moneda` | CO / COP | Para el canal (R7) |
| `cuenta_registrada` | `****-4521` | Ficticia |
| `canal_preferido` | `PSE` | Solo sugerencia |
| `acuerdo_monto` | 4.500.000 | Base de R3.2 a R3.4 |
| `estado` | `ACTIVO` | Ver RV2 |
| `prioridad` | `B` | Ver RV3 |
| `actualizado_por` / `actualizado_en` | | Para el acta |

## Requisitos

### RV1. Base de proveedores
**Historia:** como administrador de proveedores, quiero una sola tabla que diga a quién se le puede pagar y a qué cuenta.

- **RV1.1** EL SISTEMA DEBERÁ guardar a cada proveedor con los campos de la tabla anterior, validados con un esquema cerrado.
- **RV1.2** EL MOTOR DE REGLAS DEBERÁ leer de esta tabla la lista permitida (R4.1), la cuenta registrada (R4.2) y el acuerdo (R3.2 a R3.5). Lo que no esté en la tabla se trata como beneficiario no permitido.
- **RV1.3** EL SISTEMA DEBERÁ ofrecer solo lectura al agente de entrada y al agente de reglas. **La IA no crea ni edita proveedores.**
- **RV1.4** CUANDO una persona cree o cambie un proveedor, EL SISTEMA DEBERÁ guardar quién lo hizo y cuándo, y escribirlo en el acta.
- **RV1.5** CUANDO se cambie la cuenta registrada, el estado o el acuerdo de un proveedor, EL SISTEMA DEBERÁ exigir la firma del senior (cuenta y estado) o de la persona de finanzas (el resto). Agregar un proveedor cuenta como regla que afloja (R9.4).

### RV2. Estado
**Historia:** como persona de finanzas, quiero bloquear a un proveedor y que nada salga hacia él.

- **RV2.1** CUANDO el proveedor esté `BLOQUEADO`, EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «proveedor bloqueado», sin importar el monto ni la prioridad.
- **RV2.2** CUANDO el proveedor esté `NUEVO`, EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `SENIOR` (igual que R4.1).
- **RV2.3** Solo un proveedor `ACTIVO` podrá llegar a `PAGAR`.

### RV3. Prioridad
**Historia:** como persona de finanzas, quiero atender primero lo urgente sin saltarme ningún control.

- **RV3.1** EL SISTEMA DEBERÁ usar la prioridad **solo** para: ordenar la cola de aprobación, ordenar el calendario, y repartir el presupuesto cuando no alcance para todo lo pendiente.
- **RV3.2** EL MOTOR DE REGLAS DEBERÁ ignorar la prioridad al decidir, al asignar el nivel y al calcular límites. Para la misma ficha, dos proveedores con distinta prioridad y mismos demás datos DEBERÁN recibir la misma decisión y el mismo nivel.
- **RV3.3** CUANDO dos casos tengan igual prioridad, EL SISTEMA DEBERÁ ordenarlos por fecha de vencimiento y después por monto.
- **RV3.4** CUANDO el presupuesto restante no alcance para todo lo pendiente de aprobación, EL SISTEMA DEBERÁ marcar primero lo de prioridad A y mostrar lo que queda fuera del presupuesto, sin aprobar nada por sí mismo.
- **RV3.5** SI el proveedor no tiene prioridad, ENTONCES EL SISTEMA DEBERÁ tratarlo como `C`.
- **RV3.6** EL SISTEMA NO DEBERÁ mostrar la prioridad al proveedor (Panel 1).
- **RV3.7** CUANDO cambie la prioridad de un proveedor, EL SISTEMA DEBERÁ bastar con la confirmación de la persona de finanzas, porque no afloja ningún control.

### RV4. Calidad
- **RV4.1** Cada criterio DEBERÁ tener al menos una prueba automática.
- **RV4.2** PARA cualquier ficha y cualquier par de prioridades, la decisión y el nivel NO DEBERÁN cambiar (prueba de propiedades de RV3.2).

## Cambios a la spec del motor de reglas

| Criterio del motor | Cambio |
|---|---|
| R4.1, R4.2, R3.2 a R3.5 | Los datos salen de la tabla `proveedores` (RV1.2). |
| `Contexto` | Reemplaza `registros.yaml` (beneficiarios, cuentas, acuerdos) por `proveedores`. |
| R3 | Nuevo criterio de frenar: proveedor `BLOQUEADO` (RV2.1). |

## Decisiones abiertas

| # | Pregunta | Propuesta por defecto |
|---|---|---|
| DV1 | ¿«Prioridad» es urgencia de pago o confianza del proveedor? | Urgencia. La confianza sería otro campo que solo podría **endurecer** controles. |
| DV2 | ¿Cuántos niveles de prioridad? | Tres: A, B, C. |
| DV3 | ¿Dónde vive la tabla? | La base de datos del proyecto (SQLite en local, PostgreSQL en Railway). Para la entrega se carga desde `data/proveedores.yaml`. |
| DV4 | ¿El estado `NUEVO` pasa solo a `ACTIVO`? | No. Lo cambia una persona con firma del senior (RV1.5). |
