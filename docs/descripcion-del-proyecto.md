# Colombiadevs · Descripción del proyecto

**Un guardián de facturas para las empresas clientes de Blinka.** Lee las facturas de los proveedores, decide si **pagar, frenar o escalar a una persona** según las reglas de la empresa, y explica cada decisión. Es la capa de control **antes** del pago: no mueve dinero y solo usa datos ficticios.

Hecho para el *Reto Blinka, «Agentes que pagan por la empresa»* (Hackathon 30X). Demo en línea: https://colombiadevs-production.up.railway.app/

## El problema

Una empresa recibe facturas de muchos proveedores, cada una con su formato (PDF, foto, XML), y alguien debe decidir cuáles pagar. Un error significa pagar de más, pagar dos veces o pagarle a quien no era. Si se le deja la decisión a una IA, un error cuesta dinero y la IA se puede engañar con texto escrito dentro de la factura.

## Qué hace hoy

- **Lee facturas** en PDF, foto, correo, texto y XML de factura electrónica (Colombia, Perú, México, Ecuador, Uruguay, Brasil, Chile, Costa Rica y Paraguay). Una IA (Gemini o Claude, intercambiables) las lee y una **segunda lectura sin IA** comprueba que no se equivocó. Si falta un dato, el agente le pregunta al proveedor (máximo dos turnos).
- **Decide con un motor de reglas sin IA.** Compara cada factura con el registro de proveedores, el calendario de facturas esperadas, las órdenes de compra, los montos acordados y los límites de la empresa. Responde **PAGAR**, **FRENAR** o **ESCALAR**, el nivel de aprobación que hace falta (persona o senior) y un canal de pago sugerido. Ante la duda, escala: nunca paga.
- **Registra todo en un acta** de solo añadir, con una cadena de huellas que delata cualquier alteración. De ahí salen el tablero, los CSV y el archivo `pagos_aprobados.csv` que Blinka usaría para pagar.
- **Tiene dos pantallas.** «Envía facturas» (el proveedor sube facturas y ve solo el estado) y el panel de finanzas (tablero, cola de aprobación, calendario de 12 meses, acta, reglas y órdenes de compra). Entra por defecto como persona de finanzas y muestra un punto rojo con el número de aprobaciones pendientes sobre el rol que debe atenderlas.
- **Las reglas se pueden cambiar con texto** («sube el presupuesto un 20 %»): la IA solo propone y rellena el formulario; la vista previa, el techo duro, el motivo y la firma del senior para aflojar una regla son los de siempre.
- **Resultados medidos:** 29 de 29 casos de prueba con la decisión esperada, **0 pagos indebidos** y todas las decisiones con su motivo (`python3 eval.py`), más más de 550 pruebas automáticas.

## Cómo funciona

1. El proveedor sube la factura. 2. La IA la lee y una segunda lectura sin IA la verifica; lo dudoso se le pregunta al proveedor. 3. El agente entrega una **ficha** de datos al motor de reglas. 4. El motor decide y escribe en el acta. 5. Si queda en ESCALAR, una persona o un senior aprueba o rechaza escribiendo un motivo. 6. Las aprobadas salen en el archivo de pagos.

**Principio central:** la IA solo lee y propone; **quien decide es código**. Todo lo que viene de fuera (la factura, el chat) es un dato, nunca una instrucción. Dato faltante, error o duda: ESCALAR.

## Qué se desea lograr a futuro

- **Datos reales de Blinka:** el formato real del archivo de pagos, las órdenes de compra reales y la moneda de los límites de cada cliente (hoy son supuestos).
- **Verificación con la autoridad tributaria** (DIAN, SUNAT) y revisión de cumplimiento tipo Sarlaft.
- **Contratos:** subir un contrato y que el sistema proponga el calendario de pagos, que una persona confirma.
- **Presupuesto y análisis por centro de costos y por proveedor**, para acercarse a un equipo de compras «agentizado».
- **Integración con ERP y contabilidad** (QuickBooks y otros), y un **servidor MCP** propio de solo consulta y propuesta, nunca de decisión ni de pago.
- **Más robustez:** PostgreSQL con permisos, conciliación automática del acta y casos de prueba escritos por otras personas.

## Lo que no hace (a propósito)

No mueve dinero real, no abre cuentas ni verifica identidades, no usa datos reales, no tiene inicio de sesión (el rol es un selector de demostración) y no consulta a ninguna autoridad tributaria todavía.

Más detalle: [`README.md`](../README.md) · [`AVANCES.md`](../AVANCES.md) · [`specs/README.md`](../specs/README.md)
