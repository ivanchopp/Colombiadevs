# Requisitos: extracción y agente de entrada

Estado: **borrador para revisión del equipo**.
Base: «Ruta de una factura» (pasos 1 a 4 del camino de una factura) y las specs `motor-de-reglas` y `paneles-y-despliegue`.

## Resumen

El agente de entrada recibe la factura que sube el proveedor (en el Panel 1), la **lee** con IA, la **verifica** con una segunda lectura sin IA, **pregunta** lo dudoso (máximo 2 turnos) y entrega una **ficha** estándar al motor de reglas. **No decide nada.** Todo lo que viene de fuera (el archivo y el chat) es un **dato no confiable**: se lee, nunca se obedece.

## Alcance

**Dentro:** validar el archivo, leer, segunda lectura, detectar órdenes escondidas, preguntar, armar la ficha, llamar al motor, estado de entrada y modo demo.

**Fuera:** decidir pagar, frenar o escalar (`motor-de-reglas`), el acta (`acta-y-csv`), el agente de reglas y el de conciliación (capa 3).

## Parámetros por defecto (supuestos)

| Parámetro | Valor |
|---|---|
| `tamano_max_bytes` | 5 MB |
| `tipos_permitidos` | PDF, JPG, PNG, EML, TXT |
| `facturas_max_por_sala` | 5 (se cambia con la variable `FACTURAS_MAX`, EA1.5) |
| `turnos_max` | 2 |
| `largo_max_mensaje` | 500 caracteres |
| Modelo de lectura (Claude) | `claude-sonnet-5-5` (cambia con `MODELO_ENTRADA`) |
| Modelo de lectura (Gemini) | `gemini-3.8-flash` (cambia con `MODELO_GEMINI`; verificado en Railway el 17 oct: `gemini-2.5-flash` ya no está disponible) |

## Requisitos

### EA1. Recepción del archivo
- **EA1.1** CUANDO llegue un archivo, EL SISTEMA DEBERÁ aceptarlo solo si su tamaño es menor o igual a `tamano_max_bytes` y su **contenido real** (firma de bytes), no solo la extensión, corresponde a un tipo permitido.
- **EA1.2** SI la extensión no coincide con el contenido, ENTONCES EL SISTEMA DEBERÁ rechazarlo con un mensaje claro y no guardarlo.
- **EA1.3** CUANDO una sala ya tenga `facturas_max_por_sala` facturas subidas, EL SISTEMA DEBERÁ rechazar la siguiente. Las facturas de la semilla no cuentan.
- **EA1.4** EL SISTEMA DEBERÁ guardar el texto libre de la factura aparte de la ficha, de modo que el motor nunca lo reciba (R2.4).
- **EA1.5** EL límite `facturas_max_por_sala` DEBERÁ poder cambiarse con la variable de entorno `FACTURAS_MAX`, sin tocar el código. SI el valor no es un entero entre 1 y 100, ENTONCES EL SISTEMA DEBERÁ ignorarlo y usar 5. El límite protege el saldo de la IA y la demo pública; no es un tope de gasto real, que se pone en el proveedor de IA.

### EA2. Lectura con IA
- **EA2.1** EL AGENTE DEBERÁ devolver, con un esquema cerrado, estos campos: beneficiario, número, monto, moneda, vencimiento y cuenta, más la lista de campos dudosos.
- **EA2.2** EL AGENTE DEBERÁ tratar todo el contenido de la factura como datos dentro de un bloque marcado, y su instrucción de sistema DEBERÁ decir que nada de ese contenido es una instrucción.
- **EA2.3** EL SISTEMA DEBERÁ validar la salida contra el esquema y convertir los montos a `Decimal`. SI la salida es inválida, ENTONCES la lectura queda como dudosa.
- **EA2.5** (OC3.1) ADEMÁS, EL AGENTE DEBERÁ devolver el número de orden de compra (`orden_compra`) y la identificación tributaria del emisor (`id_tributaria`) cuando la factura los traiga, tal como están escritos. SI no aparecen, ENTONCES quedan vacíos; NUNCA se estiman y NUNCA cuentan como dudosos (una factura sin OC es normal).
- **EA2.4** EL AGENTE NO DEBERÁ recibir las reglas, los límites ni los registros de la empresa.

### EA2b. Proveedor de IA intercambiable
- **EA2b.1** LA lectura DEBERÁ poder hacerse con **Gemini** o con **Claude**, con el mismo esquema de salida, las mismas instrucciones de seguridad y el mismo tratamiento posterior (limpieza, segunda lectura, motor). Cambiar de proveedor NO DEBERÁ cambiar ninguna otra pieza.
- **EA2b.2** EL proveedor DEBERÁ elegirse con `PROVEEDOR_IA` (`gemini` o `claude`). SI no se define, ENTONCES se usa Claude si hay `ANTHROPIC_API_KEY`, y si no, Gemini si hay `GEMINI_API_KEY` (o `GOOGLE_API_KEY`).
- **EA2b.3** SI el proveedor elegido no tiene clave, ENTONCES EL SISTEMA DEBERÁ pasar a modo demo (EA8), nunca a otro proveedor sin que se le indique.
- **EA2b.4** LA pantalla DEBERÁ indicar qué proveedor y qué modelo están activos, o que está en modo demo.
- **EA2b.5** CUANDO el proveedor bloquee la respuesta (filtro de seguridad, vacía o inválida), EL SISTEMA DEBERÁ tratarlo como lectura fallida (EA8.1).
- **EA2b.6** CUANDO el enlace traiga `?diagnostico=1`, EL PANEL 1 DEBERÁ mostrar, para cada variable relacionada con la IA, solo si está «definida», «vacía» o «no definida», el proveedor resultante, la razón por la que está en modo demo y, si existen, el entorno, el servicio y el commit del despliegue. NUNCA DEBERÁ mostrar el valor de una clave.
- **EA2b.7** EL diagnóstico DEBERÁ listar, solo por nombre, las variables del entorno que parezcan una clave de Gemini, Google o Anthropic (por ejemplo `GEMINI_APY_KEY`) pero no sean las esperadas, para detectar errores de escritura. NO DEBERÁ marcar claves de otros servicios (por ejemplo `MAPBOX_API_KEY`).
- **EA2b.8** EL SISTEMA DEBERÁ ignorar los espacios al inicio y al final de una clave, y tratar una clave de solo espacios como vacía.
- **EA2b.9** CUANDO la lectura con IA falle y el sistema degrade a la lectura por patrones (EA8.1), EL SISTEMA DEBERÁ dejar el error en el registro del servidor (los Logs de Railway), sin ningún valor de clave, para que quien administre la demo vea que la IA no está respondiendo aunque la pantalla diga que está activa.
- **EA2b.10** (R6) EL diagnóstico (`?diagnostico=1`) DEBERÁ mostrar la **última falla de lectura con IA** (hora, proveedor y mensaje, sin ningún valor de clave), para ver la causa sin abrir los Logs. Una falla degrada en silencio la factura a patrones (EA8.1), y por eso una app con la IA «activa» puede no estar leyendo con IA.
- **EA2b.11** (R6) EL diagnóstico DEBERÁ ofrecer un botón «Probar la conexión con la IA ahora» que haga **una** lectura mínima con el proveedor activo y muestre el resultado o el error (sin claves) y, para Gemini, los nombres de los modelos disponibles para elegir `MODELO_GEMINI`. NO DEBERÁ aparecer sin el parámetro.

### EA3. Segunda lectura (sin IA)
- **EA3.1** EL SISTEMA DEBERÁ extraer el texto (PDF, EML, TXT) y buscar con patrones de texto el beneficiario, el monto, la moneda y el vencimiento.
- **EA3.2** EL SISTEMA DEBERÁ marcar la ficha con `segunda_lectura = coincide` solo si encontró los cuatro campos y todos coinciden con la lectura de la IA. En cualquier otro caso, `no_coincide`, y los campos que difieren pasan a la lista de dudosos.
- **EA3.3** CUANDO el archivo sea una imagen (sin texto extraíble), EL SISTEMA DEBERÁ marcar `segunda_lectura = no_disponible`, y lo mismo CUANDO el texto no contenga ninguno de los cuatro campos comparables. El motor escala (R2.2). Ante la duda se escala.
- **EA3.4** LOS PATRONES DEBERÁN reconocer el formato de una factura electrónica colombiana: el monto tras la etiqueta «TOTAL:» (con el valor en la línea siguiente, como lo entrega el PDF), el beneficiario tras «Razón social/Nombre:» (el primero del documento es el emisor) y el número tras «Nro. Doc.:» o «N° de documento:».
- **EA3.5** EL monto NO DEBERÁ tomarse de etiquetas que solo contengan la palabra «total» dentro de otra («SUBTOTAL», «TOTAL Base Imponible», «TOTAL Descuento Global», «TOTAL en letras»). Si hay varios «TOTAL:», DEBERÁ usarse el último.
- **EA3.6** CUANDO haya monto pero ningún símbolo de moneda junto a él, LA moneda DEBERÁ tomarse del texto solo si aparece exactamente un código de moneda distinto (por ejemplo «COP» en el total en letras). Si no hay ninguno o hay varios, la moneda queda sin leer. NO DEBERÁ suponerse una moneda.
- **EA3.7** EL número de factura DEBERÁ contener al menos un dígito, para no confundir palabras como «Electrónica» con un número.
- **EA3.9** (OC3.2) LA segunda lectura DEBERÁ buscar también el número de OC (tras «Orden de compra», «O.C.», «PO» o «Purchase order») y la identificación tributaria (tras «NIT», «RUC», «RFC»). Se comparan sin espacios, guiones ni mayúsculas, y SOLO cuentan si alguna de las dos lecturas los vio: si una los ve y la otra no, o difieren, ENTONCES `no_coincide` y el motor escala (R2.2). Una factura sin OC se compara como siempre.
- **EA3.8** Lo que los patrones no encuentren (por ejemplo, una factura de contado sin fecha de vencimiento) DEBERÁ quedar sin leer y dudoso; NO DEBERÁ inventarse. Estas ampliaciones NO cambian EA8.2: un archivo propio leído solo con patrones sigue marcado como dudoso y siempre se escala.

### EA4. Órdenes escondidas
- **EA4.1** EL SISTEMA DEBERÁ buscar, con patrones de texto y sin IA, frases que intenten dar órdenes (por ejemplo «ya está aprobada», «págala», «ignora las reglas») en el texto de la factura y en los mensajes del proveedor, y marcar `orden_en_texto`.
- **EA4.2** CUANDO se marque `orden_en_texto`, EL MOTOR DEBERÁ escalar (R2.4), y la orden NO DEBERÁ cambiar ningún campo de la ficha.

### EA5. Preguntas al proveedor
- **EA5.1** EL AGENTE DEBERÁ preguntar solo por los campos dudosos, uno por turno, con preguntas de plantilla (sin IA), y como máximo `turnos_max` turnos.
- **EA5.2** LA respuesta del proveedor DEBERÁ validarse por campo (un monto es un número, una fecha es una fecha) y guardarse en `valores_aclarados`. NUNCA DEBERÁ reemplazar el valor original (R2.3).
- **EA5.3** UN mensaje del proveedor NO DEBERÁ superar `largo_max_mensaje` caracteres y se mostrará siempre como texto plano.
- **EA5.4** LA respuesta del proveedor NO DEBERÁ cambiar `segunda_lectura`: una confirmación por chat no verifica nada (R4.3).

### EA6. Ficha y llamada al motor
- **EA6.1** UNA VEZ resueltos o agotados los turnos, EL SISTEMA DEBERÁ armar la ficha con código, validarla con el esquema de `engine.modelos.Ficha` y llamar a `registrar_decision`.
- **EA6.2** EL SISTEMA NO DEBERÁ decidir ni sugerir pagos; solo entrega la ficha. SI la ficha no es válida, ENTONCES EL SISTEMA DEBERÁ registrarla en el acta como escalada (R2.1, R8.6), de modo que una persona la vea en el Panel 2, e informar al proveedor que quedó en revisión manual. NUNCA DEBERÁ dejar una factura que el proveedor ve «en revisión» sin que finanzas la vea.
- **EA6.4** SI un dato original no se pudo leer y el proveedor lo aclaró, ENTONCES EL SISTEMA DEBERÁ usar lo aclarado, marcar ese campo con `origen_campos = aclarado` (el motor lo trata según R2.5) y dejar `lectura_ia = dudosa`, de modo que se escale. SI aun así falta algún dato obligatorio, ENTONCES la ficha es inválida y se registra como escalada «en revisión manual» (EA6.2).
- **EA6.3** EL `preparador` DEBERÁ ser el código de la sala (separación de funciones, R8.2).

### EA7. Estado de entrada
- **EA7.1** EL SISTEMA DEBERÁ llevar el estado de cada factura en la entrada: «recibida» (esperando respuesta), «datos confirmados» (lista para el motor).
- **EA7.2** UNA VEZ registrada la decisión, EL ESTADO PÚBLICO DEBERÁ salir del acta («en revisión» o «resuelta», AC4.3) y NO DEBERÁ incluir motivos ni reglas.

### EA8. Modo demo
- **EA8.1** SI no hay clave de la API, o la llamada falla, o `ENTRADA_MODO=demo`, ENTONCES EL SISTEMA DEBERÁ leer con patrones de texto (EA8.2). Las lecturas guardadas de las cuatro facturas de ejemplo solo se usan en pruebas y evaluación (EA8.4).
- **EA8.4** LAS lecturas guardadas de las cuatro facturas de ejemplo (EA8.1) DEBERÁN quedar solo para las pruebas automáticas y la evaluación; el Panel 1 NO DEBERÁ tener ningún camino que las use (PP2.4). En la app, un archivo se lee con la IA o, sin ella, con los patrones de texto (EA8.2).
- **EA8.2** CUANDO se suba un archivo propio en modo demo, EL SISTEMA DEBERÁ leerlo solo con los patrones de texto y marcar `lectura_ia = dudosa`, de modo que **siempre se escale**.
- **EA8.3** EL SISTEMA DEBERÁ avisar en pantalla cuando esté en modo demo.

### EA10. Factura electrónica en XML y verificación local del NIT
**Historia:** como cliente de Blinka, quiero subir el XML de la factura electrónica, que se lee sin errores y sin gastar IA, y que el sistema desconfíe de un NIT con el dígito de verificación mal puesto.

- **EA10.1** EL SISTEMA DEBERÁ aceptar archivos `.xml` (tipo `xml`) de hasta 5 MB y DEBERÁ rechazar un `.xml` cuyo contenido no sea una factura UBL (`Invoice`) o un `AttachedDocument` de la DIAN que la contenga.
- **EA10.2** EL SISTEMA DEBERÁ leer el XML con un analizador estructural, sin IA: beneficiario (razón social del emisor), número (`cbc:ID`), monto y moneda (`cac:LegalMonetaryTotal/cbc:PayableAmount` y su `currencyID`), vencimiento (`cbc:DueDate` o `cbc:PaymentDueDate`) e identificación tributaria del emisor. EL SISTEMA NO DEBERÁ usar la IA para un XML.
- **EA10.3** EL SISTEMA DEBERÁ rechazar un XML que declare un `DOCTYPE` o una `ENTITY`, para evitar ataques de entidades externas o de expansión; las facturas electrónicas no los usan. NINGÚN dato del XML DEBERÁ interpretarse como instrucción (EA2.2).
- **EA10.4** EL SISTEMA DEBERÁ hacer la segunda lectura de un XML con un método distinto del analizador (patrones de texto sobre las etiquetas, EA3) y marcar `coincide` solo si encuentra los cuatro campos comparables y todos coinciden (EA3.2).
- **EA10.5** EL SISTEMA DEBERÁ calcular localmente el dígito de verificación de un NIT colombiano (módulo 11, pesos 3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67 y 71). SI el NIT del emisor trae su dígito y no coincide con el calculado, ENTONCES la lectura DEBERÁ quedar `dudosa` y la factura DEBERÁ escalarse; NUNCA `PAGAR`.
- **EA10.6** EN una factura de la DIAN (perfil `DIAN 2.1`), EL SISTEMA DEBERÁ exigir el CUFE (`cbc:UUID`). SI falta, ENTONCES la lectura DEBERÁ quedar `dudosa`. En otros países no se exige.
- **EA10.7** LA verificación del NIT DEBERÁ aplicarse también al primer NIT con su dígito que aparezca en el texto de un PDF, correo o texto; SI no hay NIT con dígito, NO DEBERÁ afectar la lectura.
- **EA10.8** EL sistema NO consulta a la DIAN ni a otra autoridad: que el dígito sea correcto **no prueba** que la factura sea válida ni que el NIT exista. Esa consulta queda en el roadmap (R10). Ningún texto de pantalla DEBERÁ afirmar que la factura «está validada por la DIAN».
- **EA10.9** EL NIT leído DEBERÁ guardarse en el estado de la entrada (`id_tributaria`) para las órdenes de compra; NO DEBERÁ entrar a la ficha del motor hasta que esa spec lo pida.

### EA11. Factura electrónica de México (CFDI)
**Historia:** como cliente de Blinka con proveedores en México, quiero subir el XML de su CFDI y que se lea igual que una factura colombiana, con las mismas desconfianzas.

- **EA11.1** EL SISTEMA DEBERÁ aceptar también el XML de un `Comprobante` CFDI (versiones 3.3 y 4.0, espacios de nombres `http://www.sat.gob.mx/cfd/3` y `/4`) como factura, además de UBL (EA10.1). EL SISTEMA NO DEBERÁ usar la IA para él (EA10.2) y DEBERÁ aplicar las mismas guardas contra `DOCTYPE` y `ENTITY` (EA10.3).
- **EA11.2** EL SISTEMA DEBERÁ aceptar solo un `Comprobante` de tipo `I` (ingreso). SI es de otro tipo (`E` egreso o nota de crédito, `P` pago, `T` traslado, `N` nómina), ENTONCES DEBERÁ rechazarlo con una explicación: una nota de crédito no es una factura por pagar.
- **EA11.3** EL SISTEMA DEBERÁ leer del CFDI: beneficiario (`Emisor@Nombre`), número (`Serie` y `Folio`, unidos con guion, o solo `Folio`), monto (`Total`), moneda (`Moneda`) e identificación tributaria del emisor (`Emisor@Rfc`). SI falta el folio, ENTONCES el número queda sin leer y dudoso; NO DEBERÁ sustituirse por el UUID.
- **EA11.4** UN CFDI NO trae fecha de vencimiento. EL vencimiento DEBERÁ quedar sin leer y dudoso, y EL agente DEBERÁ preguntarlo al proveedor (EA3.8). NO DEBERÁ interpretarse el texto de `CondicionesDePago`.
- **EA11.5** SI la moneda es `XXX` (sin moneda) o no es un código de tres letras, ENTONCES la moneda DEBERÁ quedar sin leer y dudosa. NO DEBERÁ suponerse una moneda.
- **EA11.6** EL SISTEMA DEBERÁ revisar en local el RFC del emisor: formato de persona moral (12 caracteres) o física (13) y su dígito verificador (módulo 11). SI el formato o el dígito no cuadran, o es un RFC genérico (`XAXX010101000`, `XEXX010101000`), ENTONCES la lectura DEBERÁ quedar `dudosa` y la factura DEBERÁ escalarse; NUNCA `PAGAR` (como EA10.5).
- **EA11.7** EN un CFDI, EL SISTEMA DEBERÁ exigir el UUID del `TimbreFiscalDigital`. SI falta, ENTONCES la lectura DEBERÁ quedar `dudosa` (como EA10.6).
- **EA11.8** LA segunda lectura DEBERÁ hacerse con patrones de texto sobre los atributos, un método distinto del analizador, y comparar los mismos campos que en EA10.4. EL RFC DEBERÁ compararse como la identificación tributaria (EA3.9).
- **EA11.9** EL sistema NO consulta al SAT: un RFC con el dígito correcto o un UUID presente **no prueban** que la factura sea válida (roadmap R10). NO DEBERÁ revisar que la moneda corresponda al país del proveedor (AVANCES P33): una factura en MXN de un proveedor de otro país solo se convierte con la tabla de cambio.

### EA9. Calidad
- **EA9.1** Cada criterio DEBERÁ tener una prueba automática, sin red y sin clave, usando un cliente falso para la IA.
- **EA9.2** UNA prueba DEBERÁ comprobar que las cuatro facturas de ejemplo producen la decisión esperada: normal → `PAGAR`, repetida → `FRENAR`, beneficiario nuevo → `ESCALAR` al senior, orden escondida → `ESCALAR`.
- **EA9.3** UNA prueba DEBERÁ comprobar que ningún texto de factura o de chat, por más que ordene aprobar, produce `PAGAR`.

## Decisiones abiertas

| # | Pregunta | Propuesta por defecto |
|---|---|---|
| DE1 | ¿La confirmación por chat puede devolver `coincide`? | No (EA5.4): lo dicho por chat no verifica |
| DE2 | ¿El agente pregunta por la cuenta bancaria? | No en esta versión: la cuenta se compara solo con los registros |
| DE3 | ¿Modelo de lectura? | `claude-sonnet-5-5` o `gemini-2.5-flash`; verificar los nombres vigentes antes de la entrega (P4) |
| DE4 | ¿Datos enviados a Gemini? | Solo facturas ficticias. Los planes gratuitos de Gemini pueden usar lo enviado para mejorar el producto: no subir datos reales |
