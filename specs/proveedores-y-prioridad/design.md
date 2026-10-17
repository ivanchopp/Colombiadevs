# Diseño: base de proveedores y prioridad

Estado: **borrador para revisión del equipo**.
Parte de `specs/motor-de-reglas/design.md`; solo describe lo que cambia.

## Modelo

```python
class Proveedor(BaseModel):
    id: str
    nombre: str
    documento_tributario: str            # ficticio, «supuesto»
    pais: str
    moneda: str
    cuenta_registrada: str
    canal_preferido: str | None
    acuerdo_monto: Decimal | None
    estado: Literal["NUEVO", "ACTIVO", "BLOQUEADO"]
    prioridad: Literal["A", "B", "C"] = "C"
    actualizado_por: str
    actualizado_en: datetime
```

`Contexto.proveedores: dict[str, Proveedor]` reemplaza a los beneficiarios, cuentas y acuerdos sueltos.

## Revisión nueva

`proveedor_estado` en `engine/revisiones/beneficiario.py`, antes de la lista permitida:

| Estado | Efecto |
|---|---|
| `BLOQUEADO` | `FRENAR`, «proveedor bloqueado» (RV2.1) |
| `NUEVO` | `ESCALAR`, nivel `SENIOR` (RV2.2) |
| `ACTIVO` | `OK` |
| no existe | `ESCALAR`, nivel `SENIOR` (R4.1) |

## Dónde se usa la prioridad (y dónde no)

La prioridad **no entra en `engine/`**. El módulo `evaluar` no la recibe, así RV3.2 se cumple por construcción: la función no puede usar lo que no ve.

Solo la leen estas piezas, fuera del motor:

- `app/cola.py`: ordena por `(prioridad, vence, monto)` (RV3.1, RV3.3).
- `app/calendario.py`: mismo orden.
- `app/presupuesto.py`: dado el presupuesto restante y los casos pendientes, devuelve cuáles caben por orden de prioridad (RV3.4). Solo informa; la aprobación sigue siendo humana.

## Datos

`data/proveedores.yaml` con 12 proveedores ficticios para la demo: mezcla de prioridades A, B y C, un `NUEVO`, un `BLOQUEADO` y uno con cuenta distinta a la de una factura de prueba. Todo marcado «supuesto».

## Estrategia de pruebas

- Una prueba por criterio.
- **Propiedad clave (RV4.2):** para cualquier ficha y cualquier par de prioridades, el `Resultado` es idéntico.
- Prueba de arquitectura: `engine/` no importa nada de `app/` ni lee el campo `prioridad`.
- Caso trampa: proveedor `BLOQUEADO` con prioridad A sigue frenado.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| La prioridad se usa para saltarse un control | No entra al motor; prueba de propiedades (RV4.2) |
| La IA cambia una cuenta o un estado | Solo lectura para los agentes (RV1.3); cambios con firma (RV1.5) |
| Datos del maestro desactualizados | Lo que no está registrado se escala (RV1.2) |
