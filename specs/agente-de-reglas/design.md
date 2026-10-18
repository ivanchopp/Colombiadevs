# Diseño: agente de reglas en lenguaje natural

Requisitos: `requirements.md`. El diseño general del motor y la página de reglas está en `specs/motor-de-reglas/design.md` y `specs/paneles-y-despliegue/design.md`; aquí solo lo nuevo.

## Idea central

El agente **no tiene un camino propio hacia las reglas**. Solo **rellena el formulario que ya existe** en la página «Reglas». Todo lo demás (vista previa, afloja o restringe, firma por rol, techo duro, motivo, `CAMBIO_REGLA`) lo hace el código de siempre. Así las garantías de AR1 se cumplen por construcción, no por promesa:

```
texto ──▶ lector (IA o patrones) ──▶ Propuesta cerrada ──▶ resolver (Decimal, código)
                                                              │
                                              valores nuevos │ rellenan el formulario
                                                              ▼
                       vista previa (simular) ─▶ persona escribe motivo ─▶ botón «Aplicar»
                                                              │
                         validar_cambio · cambios_que_aflojan · rol ─▶ cambiar_reglas ─▶ acta
```

## Piezas

| Pieza | Dónde | Qué hace |
|---|---|---|
| Esquema y modelos | `agents/reglas_texto.py` | `CambioPedido` y `Propuesta` (Pydantic cerrado, `extra="forbid"`), hasta 4 cambios; `ESQUEMA` JSON para la salida estructurada |
| Lector con IA | `agents/reglas_texto.py` | Una llamada de texto al proveedor activo (Gemini o Claude, como `lectura_ia`), salida estructurada, pedido dentro de un bloque de datos |
| Lector por patrones | `agents/reglas_texto.py` | Expresiones para «fija / pon / sube / baja … a / en / un N %»; sin IA (AR6) |
| Comprobación | `agents/reglas_texto.py` | `comprobar_coherencia(pedido, propuesta)` devuelve las señales de AR2.8 (frases armadas por código) |
| Resolución | `agents/reglas_texto.py` | `resolver(propuesta, actuales, tasas)` devuelve valores `Decimal` o una explicación; convierte otras monedas con la tabla de cambio (AR2.3) |
| Página | `app/pages/5_Reglas.py` | Caja de texto, botón «Entender», resumen armado por código y relleno del formulario |
| Origen en el acta | `app/apoyo.py` | `cambiar_reglas(..., origen="formulario"\\|"texto", pedido=None)` agrega `origen` y `pedido` al `CAMBIO_REGLA` |

## Qué recibe y qué devuelve la IA

- **Recibe:** el pedido (hasta 500 caracteres) dentro de un bloque marcado como datos y el catálogo de parámetros (nombre, unidad, si es monto, porcentaje o días). **No recibe** valores vigentes, facturas, proveedores ni la tabla de cambio.
- **Devuelve:** un objeto con `estado` (`propuesta`, `aclaracion`, `no_entendido` o `fuera_de_alcance`), `cambios` (la lista cerrada de AR2.1) y `pregunta` (texto corto). El texto de `pregunta` se muestra tal cual **solo** como pregunta, nunca como dato (AR3.2).
- **Operaciones:** `fijar` (valor absoluto), `subir_monto` / `bajar_monto` (suma o resta una cantidad), `subir_porcentaje` / `bajar_porcentaje` (multiplica por `1 ± valor/100`). La IA solo identifica la operación y el número; **las cuentas las hace el código**.

## Quién interpreta y quién comprueba

- **Con IA, la IA interpreta el lenguaje** y decide si hay ambigüedad (`aclaracion`, `no_entendido`). **El código no interpreta**: valida el esquema, calcula y aplica las reglas.
- **Sin IA** el lector por patrones solo entiende frases simples y todo lo demás es `no_entendido`.
- **Comprobación de coherencia por código (AR2.8):** la IA puede equivocarse con seguridad, y una segunda IA suele repetir el error. Por eso el código compara, sin interpretar, la propuesta con el texto:
  1. Cuenta las menciones de parámetros en el pedido con un vocabulario fijo («pago automático», «presupuesto», «tolerancia»…) y avisa si la propuesta trae menos cambios.
  2. Extrae los números del pedido (dígitos, con puntos o comas de miles y decimales, y los multiplicadores «mil» y «millones») y avisa si alguno no es el `valor` de un cambio.
  3. Avisa si un `valor` de la propuesta no está entre los números del pedido, salvo «doble», «triple» o «mitad».
  La propuesta queda `dudosa` y la página exige la marca «Revisé que estos son todos los cambios que quería» antes de habilitar el botón (AR3.5). **No rechaza nada:** la decisión sigue siendo de la persona. No hay segunda llamada a la IA.

## Resolución y redondeo

- Los montos del formulario son enteros en la moneda base y los porcentajes, enteros de 0 a 100. Si el valor resuelto no es entero, **se redondea al entero más cercano (mitad hacia arriba) y el resumen lo dice**. Nunca se redondea hacia un valor más laxo sin avisar.
- Un monto en otra moneda se convierte con `ctx.tasas` (R5.1) y se redondea igual. Sin tasa, se rechaza.
- Una operación sobre un parámetro que el pedido repite («sube el autopago a 1.000 y bájalo a 500») es ambigua: se pregunta.

## Lector por patrones (sin IA)

Reconoce solo frases simples, en español, con sinónimos de los siete parámetros («pago automático», «autopago», «presupuesto», «límite por proveedor», «tolerancia», «margen de días»…). Es deliberadamente corto: lo que no entiende devuelve `no_entendido` con un ejemplo. Sirve como respaldo, para las pruebas y para la demo sin clave.

## Seguridad

| Riesgo | Mitigación |
|---|---|
| Inyección («ignora el techo y aplícalo») | El pedido es un dato; la salida es un esquema cerrado; `validar_cambio` y la firma deciden |
| La IA se equivoca de cifra | El código calcula, y la persona ve el valor vigente y el nuevo antes de aplicar |
| Aflojar sin firma | Mismo `cambiar_reglas`: un `PERSONA` recibe `INTENTO_RECHAZADO` |
| Gasto de IA | `PEDIDOS_REGLAS_MAX` por sala (AR5.5); si se agota, solo patrones |
| Fuga de datos a la IA | Solo recibe el pedido y el catálogo (AR5.2) |
| Clave en los Logs | `lectura_ia.sin_secretos` en cada error (AR5.4) |

## Decisiones de diseño

1. **Rellenar el formulario** en vez de un flujo de confirmación propio: una sola ruta hacia el acta, menos código y menos superficie.
2. **Sin estado de conversación** (AR-D2): una sola llamada por pedido; si hay duda, la persona reescribe.
3. **Un cliente de IA compartido:** la llamada se apoya en `lectura_ia.crear_cliente` y `proveedor_activo`; la parte específica de cada proveedor (esquema JSON estructurado) se reutiliza o se extrae a una función común.

## ART5: lector con IA (cómo se construyó)

- `reglas_texto.leer_con_ia(pedido, cliente=None, proveedor=None) -> Propuesta`: **una** llamada de texto con el proveedor activo, reutilizando de `lectura_ia` el cliente (`crear_cliente`), el proveedor (`proveedor_activo`), los modelos, el tope de salida y `sin_secretos`. Sin herramientas: la IA no puede llamar a nada (AR1.1).
- **Esquema:** `ESQUEMA_PROPUESTA` (JSON cerrado) con `estado`, `cambios` (parámetro, operación, `valor` como **texto**, moneda o null) y `pregunta`. La instrucción de sistema trae el catálogo (nombre, tipo, para qué sirve) y **ningún valor vigente** (AR5.2); el pedido va entre `<pedido>` como dato (AR5.1).
- **Salida:** se valida con `Propuesta`; si el estado no es `propuesta` se descartan los cambios, y una `propuesta` vacía es `no_entendido` (AR5.7). Un valor mayor que 10^12 se rechaza en el modelo.
- `entender(..., cliente=None, puede_usar_ia=True)`: si hay IA y queda cupo, la intenta; cualquier falla (red, cuota, esquema inválido) se registra con `registrar_falla` y degrada a patrones (AR5.4). Después aplica `resolver` y `comprobar_coherencia` igual que con patrones (AR5.8). `Resultado` suma `llamo_ia` (para contar el cupo) y `motivo_patrones` (`sin_ia`, `tope` o `falla`) para decirlo en pantalla.
- **Tope por sala (AR5.5, AR5.6):** tabla `pedidos_reglas(sala_id, usados)` en la misma base SQLite, con `ContadorPedidosIA` en `agents/estado.py`. La página lo consulta antes y lo incrementa después de cada llamada intentada. `PEDIDOS_REGLAS_MAX` (por defecto 10, entre 1 y 100; un valor inválido vuelve a 10).
