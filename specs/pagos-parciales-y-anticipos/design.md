# Diseño: pagos parciales y anticipos

Estado: **borrador para revisión del equipo**.
Parte del diseño de `specs/motor-de-reglas/design.md`; solo describe lo que cambia.

## Cambios en los modelos

```python
class Ficha(BaseModel):
    ...                                   # campos actuales
    tipo_pago: Literal["TOTAL", "PARCIAL", "ANTICIPO"]
    monto_a_pagar: Decimal                # > 0
    numero_pago: int = 1                  # 1 para TOTAL; 1, 2, 3... en parciales

class Contexto(BaseModel):
    ...
    pagado_de_factura: dict[str, Decimal]       # factura -> suma pagada o aprobada
    planes_de_cuotas: dict[str, list[Cuota]]    # factura -> cuotas registradas
    respaldos_de_anticipo: dict[str, Respaldo]  # beneficiario -> acuerdo u orden de compra
    anticipos_abiertos: dict[str, Decimal]      # beneficiario -> suma
```

## Revisiones nuevas

Se agregan a `engine/revisiones/pagos.py`. Corren todas, como las demás (R1.5).

| Revisión | Criterio | Efecto |
|---|---|---|
| `tipo_pago_valido` | RP1.2, RP1.3 | `ESCALAR` |
| `sobrepago` | RP2.1 | `FRENAR` |
| `parcial_sin_plan` | RP2.4 | `ESCALAR`, nivel `PERSONA` |
| `anticipo` | RP3.1 | `ESCALAR`, nivel `SENIOR` |
| `anticipo_sin_respaldo` | RP3.2 | `FRENAR` |
| `anticipo_limite` | RP3.3 | `FRENAR` |

Orden: después de «Tipo de cambio» y antes de «Duplicado».

## Piezas con lógica propia

**Huella (RP2.2):** `sha256(beneficiario | numero | fecha | numero_pago)`. Dos pagos distintos de la misma factura tienen huellas distintas; el mismo pago enviado dos veces, la misma.

**Nivel (RP2.6):** `monto_para_nivel = pagado_o_aprobado_del_periodo(beneficiario) + monto_a_pagar_en_base`. Es la misma fórmula de R5.2 con `monto_a_pagar` en lugar del monto de la factura. Por eso fraccionar no baja el nivel.

**Seguro por defecto (RP1.1):** mientras RP2.3 no exista, `parcial_sin_plan` no mira los planes de cuotas y siempre escala. Cuando se construya RP2.3, esa revisión pasa a `OK` solo si la cuota coincide.

## Impacto en otras piezas

- **Acta y CSV:** agregar columnas `tipo_pago`, `monto_a_pagar`, `numero_pago`, `saldo_despues`.
- **Panel 1:** el proveedor ve solo el estado; no se muestra el tipo de pago permitido ni límites.
- **Panel 2:** la cola de aprobación muestra una etiqueta «parcial» o «anticipo».
- **Agente de entrada:** puede proponer `tipo_pago` al leer la factura, pero el motor lo trata como dato sin verificar (R4.3). Un `PARCIAL` leído sin plan escala.

## Estrategia de pruebas

- Una prueba por criterio: `test_rp3_1_anticipo_escala_senior`, etc.
- Casos trampa nuevos en `data/casos.yaml`: parcial sin plan, sobrepago, anticipo sin respaldo, tres parciales de 3 M que suman más que el límite, mismo parcial enviado dos veces.
- Propiedades con Hypothesis (RP5.2, RP5.3).

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Fraccionar un pago para evitar la aprobación | R5.2 suma por beneficiario y periodo (RP2.6), con prueba propia |
| Un parcial repetido se confunde con uno nuevo | Número de pago en la huella (RP2.2) |
| Un anticipo se usa para sacar dinero sin factura | Siempre `SENIOR`, con respaldo y límite (RP3) |
| Complejidad antes de la entrega | Solo se construye el camino «escalar» |
