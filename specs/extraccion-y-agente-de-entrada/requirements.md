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
| `facturas_max_por_sala` | 5 |
| `turnos_max` | 2 |
| `largo_max_mensaje` | 500 caracteres |
| Modelo de lectura (Claude) | `claude-sonnet-5-5` (cambia con `MODELO_ENTRADA`) |
| Modelo de lectura (Gemini) | `gemini-2.5-flash` (cambia con `MODELO_GEMINI`; **sin verificar**) |

## Requisitos

### EA1. Recepción del archivo
- **EA1.1** CUANDO llegue un archivo, EL SISTEMA DEBERÁ aceptarlo solo si su tamaño es menor o igual a `tamano_max_bytes` y su **contenido real** (firma de bytes), no solo la extensión, corresponde a un tipo permitido.
- **EA1.2** SI la extensión no coincide con el contenido, ENTONCES EL SISTEMA DEBERÁ rechazarlo con un mensaje claro y no guardarlo.
- **EA1.3** CUANDO una sala ya tenga `facturas_max_por_sala` facturas subidas, EL SISTEMA DEBERÁ rechazar la siguiente. Las facturas de la semilla no cuentan.
- **EA1.4** EL SISTEMA DEBERÁ guardar el texto libre de la factura aparte de la ficha, de modo que el motor nunca lo reciba (R2.4).

### EA2. Lectura con IA
- **EA2.1** EL AGENTE DEBERÁ devolver, con un esquema cerrado, estos campos: beneficiario, número, monto, moneda, vencimiento y cuenta, más la lista de campos dudosos.
- **EA2.2** EL AGENTE DEBERÁ tratar todo el contenido de la factura como datos dentro de un bloque marcado, y su instrucción de sistema DEBERÁ decir que nada de ese contenido es una instrucción.
- **EA2.3** EL SISTEMA DEBERÁ validar la salida contra el esquema y convertir los montos a `Decimal`. SI la salida es inválida, ENTONCES la lectura queda como dudosa.
- **EA2.4** EL AGENTE NO DEBERÁ recibir las reglas, los límites ni los registros de la empresa.

### EA2b. Proveedor de IA intercambiable
- **EA2b.1** LA lectura DEBERÁ poder hacerse con **Gemini** o con **Claude**, con el mismo esquema de salida, las mismas instrucciones de seguridad y el mismo tratamiento posterior (limpieza, segunda lectura, motor). Cambiar de proveedor NO DEBERÁ cambiar ninguna otra pieza.
- **EA2b.2** EL proveedor DEBERÁ elegirse con `PROVEEDOR_IA` (`gemini` o `claude`). SI no se define, ENTONCES se usa Claude si hay `ANTHROPIC_API_KEY`, y si no, Gemini si hay `GEMINI_API_KEY` (o `GOOGLE_API_KEY`).
- **EA2b.3** SI el proveedor elegido no tiene clave, ENTONCES EL SISTEMA DEBERÁ pasar a modo demo (EA8), nunca a otro proveedor sin que se le indique.
- **EA2b.4** LA pantalla DEBERÁ indicar qué proveedor y qué modelo están activos, o que está en modo demo.
- **EA2b.5** CUANDO el proveedor bloquee la respuesta (filtro de seguridad, vacía o inválida), EL SISTEMA DEBERÁ tratarlo como lectura fallida (EA8.1).
- **EA2b.6** CUANDO el enlace traiga `?diagnostico=1`, EL PANEL 1 DEBERÁ mostrar, para cada variable relacionada con la IA, solo si está «definida», «vacía» o «no definida», el proveedor resultante, la razón por la que está en modo demo y, si existen, el entorno, el servicio y el commit del despliegue. NUNCA DEBERÁ mostrar el valor de una clave.
- **EA2b.7** EL diagnóstico DEBERÁ listar, solo por nombre, las variables del entorno que parezcan de IA (por ejemplo `GEMINI_APY_KEY`) pero no sean las esperadas, para detectar errores de escritura.
- **EA2b.8** EL SISTEMA DEBERÁ ignorar los espacios al inicio y al final de una clave, y tratar una clave de solo espacios como vacía.

### EA3. Segunda lectura (sin IA)
- **EA3.1** EL SISTEMA DEBERÁ extraer el texto (PDF, EML, TXT) y buscar con patrones de texto el beneficiario, el monto, la moneda y el vencimiento.
- **EA3.2** EL SISTEMA DEBERÁ marcar la ficha con `segunda_lectura = coincide` solo si encontró los cuatro campos y todos coinciden con la lectura de la IA. En cualquier otro caso, `no_coincide`, y los campos que difieren pasan a la lista de dudosos.
- **EA3.3** CUANDO el archivo sea una imagen (sin texto extraíble), EL SISTEMA DEBERÁ marcar `segunda_lectura = no_disponible`, y lo mismo CUANDO el texto no contenga ninguno de los cuatro campos comparables. El motor escala (R2.2). Ante la duda se escala.

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
- **EA6.2** EL SISTEMA NO DEBERÁ decidir ni sugerir pagos; solo entrega la ficha. SI la ficha no es válida, ENTONCES no se registra y se informa al proveedor que la factura quedó en revisión manual.
- **EA6.4** SI un dato original no se pudo leer y el proveedor lo aclaró, ENTONCES EL SISTEMA DEBERÁ usar lo aclarado, marcar ese campo con `origen_campos = aclarado` (el motor lo trata según R2.5) y dejar `lectura_ia = dudosa`, de modo que se escale. SI aun así falta algún dato obligatorio, ENTONCES la factura no se registra y queda en «revisión manual».
- **EA6.3** EL `preparador` DEBERÁ ser el código de la sala (separación de funciones, R8.2).

### EA7. Estado de entrada
- **EA7.1** EL SISTEMA DEBERÁ llevar el estado de cada factura en la entrada: «recibida» (esperando respuesta), «datos confirmados» (lista para el motor).
- **EA7.2** UNA VEZ registrada la decisión, EL ESTADO PÚBLICO DEBERÁ salir del acta («en revisión» o «resuelta», AC4.3) y NO DEBERÁ incluir motivos ni reglas.

### EA8. Modo demo
- **EA8.1** SI no hay clave de la API, o la llamada falla, o `ENTRADA_MODO=demo`, ENTONCES EL SISTEMA DEBERÁ usar lecturas guardadas para las cuatro facturas de ejemplo.
- **EA8.2** CUANDO se suba un archivo propio en modo demo, EL SISTEMA DEBERÁ leerlo solo con los patrones de texto y marcar `lectura_ia = dudosa`, de modo que **siempre se escale**.
- **EA8.3** EL SISTEMA DEBERÁ avisar en pantalla cuando esté en modo demo.

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
