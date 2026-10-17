# Requisitos: motor de reglas

Estado: **borrador para revisión del equipo**.
Base: documento «Ruta de una factura» (`docs/Ruta-de-una-factura.pdf`) y la guía de las 6 alternativas (`docs/Guia-6-alternativas-actualizada.pdf`).

## Resumen

El motor de reglas es el programa que **decide** qué se hace con cada factura: pagar, frenar o escalar a una persona. Es código normal, sin IA y sin red. Lee una ficha ya ordenada (la entrega el agente de entrada), la compara con los registros de la empresa, el calendario del mes y las reglas vigentes, y devuelve una decisión con su explicación.

Regla de oro: **ante la duda, el resultado es escalar, nunca pagar.** Pagar exige que todas las revisiones salgan bien.

## Alcance

**Dentro:**
- Decidir pagar, frenar o escalar, y a qué nivel (persona o senior).
- Revisar duplicados, acuerdo, presupuesto, beneficiario, cuenta, límites y calendario.
- Sugerir el canal de pago (solo recomendación).
- Validar la aprobación humana y proteger la escritura en el acta (guardarraíl).
- Cargar reglas versionadas con vigencia y detectar si un cambio afloja o restringe.
- Simular un cambio de reglas sobre las facturas recientes.

**Fuera (otras specs o fuera del reto):**
- Leer facturas y chatear con el proveedor (agente de entrada).
- Guardar el acta, generar el CSV y el tablero (spec `acta-y-csv`).
- Pantallas y despliegue (spec `paneles-y-despliegue`).
- Mover dinero real, abrir cuentas, verificar identidades, decisiones de cumplimiento o de fraude.

## Glosario

| Término | Significado |
|---|---|
| Ficha | Datos ordenados de una factura, con el valor original y el aclarado de cada campo. |
| Revisión | Resultado de una regla sobre una ficha: `OK`, `FALLA` o `AVISO`. |
| `AVISO` | No bloquea, pero impide pagar sin una persona. |
| Nivel | Quién debe aprobar: `NINGUNO` (pago automático), `PERSONA` o `SENIOR`. |
| Moneda base | Moneda en la que se comparan todos los montos (por defecto COP). |
| Periodo | Mes calendario en la zona horaria `America/Bogota`. |
| Techo duro | Límite que no se puede cambiar por chat ni aprobar desde el sistema. |
| Obligación esperada | Fila del calendario del mes: una factura que se espera recibir. |

## Parámetros por defecto

Son **valores de demostración**, editables en `reglas.yaml`. Ninguno es un dato real.

| Parámetro | Valor | Uso |
|---|---|---|
| `moneda_base` | COP | Comparar montos |
| `autopago_max` | 3.000.000 | Hasta aquí se puede pagar solo, si todo está OK |
| `persona_max` | 10.000.000 | Hasta aquí aprueba la persona de finanzas; más, el senior |
| `techo_duro_pago` | 50.000.000 | Por encima no se paga desde el sistema |
| `limite_periodo_beneficiario` | 15.000.000 | Suma máxima por beneficiario y periodo sin senior |
| `presupuesto_periodo` | 100.000.000 | Gasto máximo del periodo |
| `tolerancia_ok` | 5 % | Diferencia con lo acordado que se acepta |
| `tolerancia_frenar` | 10 % | Por encima de esto, la factura se frena |
| `ventana_dias` | ±5 | Margen de fecha para emparejar con el calendario |
| `dias_gracia` | 2 | Días después de la fecha esperada para marcar «atrasada» |

## Requisitos

Notación EARS en español: «CUANDO <evento>, EL MOTOR DE REGLAS DEBERÁ <respuesta>». También «SI <condición>, ENTONCES …».

### R1. Decisión segura
**Historia:** como persona de finanzas, quiero que ningún pago salga si no cumple todas las reglas, para confiar en el sistema.

- **R1.1** EL MOTOR DE REGLAS DEBERÁ devolver, para cada ficha, exactamente una decisión: `PAGAR`, `FRENAR` o `ESCALAR`.
- **R1.2** EL MOTOR DE REGLAS DEBERÁ devolver `PAGAR` solo CUANDO todas las revisiones obligatorias sean `OK`, ninguna sea `AVISO` y el nivel sea `NINGUNO`.
- **R1.3** SI una revisión no se puede evaluar (dato faltante, error o excepción), ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con el motivo, y nunca `PAGAR`.
- **R1.4** CUANDO haya revisiones con resultados distintos, EL MOTOR DE REGLAS DEBERÁ aplicar la decisión más severa: `FRENAR` sobre `ESCALAR`, y `ESCALAR` sobre `PAGAR`.
- **R1.5** EL MOTOR DE REGLAS DEBERÁ evaluar todas las revisiones aunque una ya haya fallado, para que el motivo muestre todas las causas.
- **R1.6** EL MOTOR DE REGLAS DEBERÁ decidir sin IA, sin red y sin ejecutar texto de la factura.
- **R1.7** PARA la misma ficha, los mismos registros y la misma versión de reglas, EL MOTOR DE REGLAS DEBERÁ devolver siempre el mismo resultado.

### R2. Entrada confiable
**Historia:** como equipo, queremos que un error de lectura o un texto engañoso nunca produzca un pago.

- **R2.1** SI la ficha no cumple el esquema cerrado, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con la revisión `FALLA` «ficha inválida».
- **R2.2** CUANDO la lectura de la IA y la segunda lectura no coincidan en beneficiario, monto, moneda o fecha de vencimiento, EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR`.
- **R2.3** CUANDO el valor aclarado de un campo difiera del original en monto o beneficiario, EL MOTOR DE REGLAS DEBERÁ marcar una diferencia y devolver `ESCALAR` con nivel `SENIOR`. Nunca reemplazará el valor original.
- **R2.4** EL MOTOR DE REGLAS DEBERÁ decidir solo con los campos estructurados de la ficha. El texto libre de la factura o del chat no cambiará ninguna decisión.

### R3. Frenar
**Historia:** como persona de finanzas, quiero que lo repetido o lo que no cuadra se frene solo, para no revisarlo a mano.

- **R3.1** CUANDO la huella de la ficha (beneficiario, número de factura, fecha y número de pago; ver `pagos-parciales-y-anticipos` RP2.2) coincida con una ya registrada, EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «repetida».
- **R3.2** CUANDO el monto no supere lo acordado más `tolerancia_ok`, EL MOTOR DE REGLAS DEBERÁ marcar la revisión `OK`.
- **R3.3** CUANDO el monto supere lo acordado más `tolerancia_ok` y no pase de `tolerancia_frenar`, EL MOTOR DE REGLAS DEBERÁ marcar `AVISO` y devolver `ESCALAR` con nivel `PERSONA`.
- **R3.4** CUANDO el monto supere lo acordado más `tolerancia_frenar`, EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «no cuadra con lo acordado».
- **R3.5** SI no existe un acuerdo registrado para el beneficiario, ENTONCES EL MOTOR DE REGLAS DEBERÁ marcar `AVISO` «sin acuerdo registrado».
- **R3.6** CUANDO el gasto del periodo más el monto de la factura supere `presupuesto_periodo`, EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «sin presupuesto».
- **R3.7** CUANDO el monto en moneda base supere `techo_duro_pago`, EL MOTOR DE REGLAS DEBERÁ devolver `FRENAR` con el motivo «supera el techo duro».

### R4. Beneficiario y cuenta
**Historia:** como senior de finanzas, quiero revisar siempre a quien cobra por primera vez o cambia de cuenta.

- **R4.1** CUANDO el beneficiario no esté en la lista permitida, EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `SENIOR`, sin importar el monto.
- **R4.2** CUANDO la cuenta aclarada sea distinta a la registrada para el beneficiario, EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `SENIOR`.
- **R4.3** EL MOTOR DE REGLAS DEBERÁ tratar lo que el proveedor diga por chat como información sin verificar. Solo los registros de la empresa sirven para verificar.

### R5. Montos, niveles y límites
**Historia:** como persona de finanzas, quiero que lo pequeño se pague solo y lo grande pase por quien corresponde.

- **R5.1** EL MOTOR DE REGLAS DEBERÁ convertir cada monto a la moneda base con la tabla de tipos de cambio y guardar la tasa usada. SI falta la tasa de una moneda, ENTONCES DEBERÁ devolver `ESCALAR` con el motivo «sin tipo de cambio».
- **R5.2** EL MOTOR DE REGLAS DEBERÁ calcular `monto_para_nivel` como la suma de lo pagado, aprobado o pendiente al mismo beneficiario en el periodo, más el monto de la factura.
- **R5.3** EL MOTOR DE REGLAS DEBERÁ asignar nivel `NINGUNO` si `monto_para_nivel` es menor o igual a `autopago_max`, `PERSONA` si es menor o igual a `persona_max`, y `SENIOR` si lo supera.
- **R5.4** CUANDO la suma del periodo para un beneficiario supere `limite_periodo_beneficiario`, EL MOTOR DE REGLAS DEBERÁ devolver `ESCALAR` con nivel `SENIOR`.
- **R5.5** CUANDO varias revisiones exijan niveles distintos, EL MOTOR DE REGLAS DEBERÁ exigir el más alto.

### R6. Calendario del mes
**Historia:** como persona de finanzas, quiero saber qué debería llegar y detectar lo inesperado.

- **R6.1** CUANDO una ficha coincida con una obligación esperada en beneficiario, monto (dentro de `tolerancia_ok`) y fecha (dentro de `ventana_dias`), EL MOTOR DE REGLAS DEBERÁ marcar la revisión `OK` y la obligación como «llegó».
- **R6.2** CUANDO una ficha no coincida con ninguna obligación, EL MOTOR DE REGLAS DEBERÁ marcar `AVISO` «inesperada» y devolver `ESCALAR` con el nivel que corresponda por R5.
- **R6.3** EL MOTOR DE REGLAS DEBERÁ emparejar cada obligación con una sola factura. Una segunda factura igual no podrá emparejarse otra vez.
- **R6.4** EL MOTOR DE REGLAS DEBERÁ calcular el estado de cada obligación: «pendiente», «llegó» o «atrasada» (pasada la fecha esperada más `dias_gracia` sin factura).

### R7. Sugerencia de canal
**Historia:** como persona de finanzas, quiero una recomendación del canal de pago más conveniente.

- **R7.1** CUANDO la decisión sea `PAGAR`, o una persona apruebe un `ESCALAR`, EL MOTOR DE REGLAS DEBERÁ devolver la lista de canales evaluados y el canal sugerido.
- **R7.2** EL MOTOR DE REGLAS DEBERÁ descartar los canales que no sirvan para el país o la moneda del beneficiario y ordenar los demás por costo, tiempo y fecha de vencimiento.
- **R7.3** SI ningún canal es compatible, ENTONCES EL MOTOR DE REGLAS DEBERÁ devolver «sin canal compatible» y avisar a la persona de finanzas.
- **R7.4** EL MOTOR DE REGLAS DEBERÁ marcar todo costo y tiempo de la tabla como «supuesto» y mostrar «sin dato» cuando falte uno. No inventará tarifas.
- **R7.5** La sugerencia NO cambiará la decisión ni enviará ningún pago.

### R8. Aprobación humana y guardarraíl
**Historia:** como equipo, queremos que ni un error de programación ni una aprobación indebida dejen salir un pago fuera de las reglas.

- **R8.1** CUANDO se invoque `registrar_decision`, EL MOTOR DE REGLAS DEBERÁ volver a evaluar todas las reglas antes de escribir en el acta. SI la decisión es `PAGAR` y alguna regla no se cumple, ENTONCES DEBERÁ rechazar la escritura y registrar el intento como error.
- **R8.2** CUANDO una persona apruebe un caso escalado, EL MOTOR DE REGLAS DEBERÁ verificar tres cosas: que su rol sea igual o mayor al nivel exigido, que haya escrito un motivo, y que no sea quien preparó el caso. SI alguna falla, ENTONCES DEBERÁ rechazar la aprobación.
- **R8.3** SI el monto supera `techo_duro_pago`, ENTONCES ninguna aprobación humana podrá convertirlo en `PAGAR`.
- **R8.4** CUANDO una persona rechace un caso escalado, EL MOTOR DE REGLAS DEBERÁ registrarlo como `RECHAZADA` con su motivo.
- **R8.5** Una aprobación humana NO podrá cambiar el monto, el beneficiario, el tipo de pago ni el monto a pagar de la ficha.

### R9. Reglas versionadas
**Historia:** como persona de finanzas, quiero cambiar las reglas por fecha sin pedirle ayuda a ingeniería.

- **R9.1** CUANDO se cargue `reglas.yaml`, EL MOTOR DE REGLAS DEBERÁ validarlo contra un esquema cerrado. SI es inválido, ENTONCES DEBERÁ conservar la última versión válida y reportar el error.
- **R9.2** EL MOTOR DE REGLAS DEBERÁ aplicar las reglas vigentes en la fecha de recepción de la factura. SI dos reglas chocan, ENTONCES gana la más específica, y a igual especificidad, la más estricta.
- **R9.3** EL MOTOR DE REGLAS DEBERÁ guardar en cada resultado la versión de las reglas aplicada.
- **R9.4** CUANDO un cambio afloje una regla (sube un umbral, un límite o el presupuesto, agrega un beneficiario o una obligación, o baja un nivel de aprobación), EL MOTOR DE REGLAS DEBERÁ exigir la firma del senior. SI solo restringe, ENTONCES bastará la confirmación de la persona de finanzas.
- **R9.5** SI un cambio supera un techo duro, ENTONCES EL MOTOR DE REGLAS DEBERÁ rechazarlo con una explicación. Los techos duros no se editan por chat.
- **R9.6** CUANDO se pida simular un cambio, EL MOTOR DE REGLAS DEBERÁ devolver qué facturas de las últimas N cambiarían de decisión, sin escribir nada.

### R10. Explicabilidad
**Historia:** como auditor, quiero entender cada decisión leyendo su registro, sin abrir el código.

- **R10.1** EL MOTOR DE REGLAS DEBERÁ devolver con cada decisión: la decisión, el nivel, la lista de revisiones (regla, resultado, valor observado, umbral y mensaje), la versión de reglas, la tasa de cambio usada y el canal sugerido.
- **R10.2** EL MOTOR DE REGLAS DEBERÁ redactar un motivo en español claro, de máximo dos frases, que nombre las causas más importantes.

### R11. Calidad
- **R11.1** Cada criterio de esta spec DEBERÁ tener al menos una prueba automática.
- **R11.2** PARA cualquier ficha generada que incumpla una regla bloqueante, la decisión NO DEBERÁ ser `PAGAR` (prueba de propiedades, «cero pagos indebidos»).
- **R11.3** Las 20 facturas de prueba DEBERÁN dar la decisión esperada (mide la autonomía).
- **R11.4** Una evaluación NO DEBERÍA tardar más de 200 ms, sin red.

## Specs relacionadas

| Spec | Qué amplía |
|---|---|
| `pagos-parciales-y-anticipos` | Pagos que no son el total de una factura. Cambia la huella (R3.1) y el estado de las obligaciones (R6). |
| `proveedores-y-prioridad` | Tabla de proveedores que reemplaza las listas sueltas de R3.5, R4.1 y R4.2, y orden por prioridad que **no** entra al motor. |

## Decisiones abiertas

| # | Pregunta | Propuesta por defecto |
|---|---|---|
| D1 | ¿«No cuadra con lo acordado» frena o escala? | Zona gris: hasta 5 % pasa; de 5 % a 10 % escala a la persona; más de 10 % frena. |
| D2 | ¿El gasto del periodo cuenta lo pendiente de aprobación? | Cuenta lo pagado y lo aprobado. Lo pendiente no, hasta que se apruebe. |
| D3 | ¿Qué es «periodo»? | Mes calendario en `America/Bogota`. |
| D4 | ¿Quién es el «preparador» para separar funciones? | Quien subió o cargó el caso en la demo, o el rol que cambió la regla. |
| D5 | ¿Los valores por defecto de la tabla anterior? | Son de demostración. Se pueden cambiar sin tocar el código. |
