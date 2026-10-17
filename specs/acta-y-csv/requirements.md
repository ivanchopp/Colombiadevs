# Requisitos: acta y CSV

Estado: **borrador para revisión del equipo**.
Base: «Ruta de una factura» (`docs/Ruta-de-una-factura.pdf`) y la spec `specs/motor-de-reglas/`.

## Resumen

El **acta** es el registro donde queda cada decisión del sistema. Solo se le añaden filas, nunca se editan ni se borran, y cada fila guarda la huella de la anterior, así cualquier cambio posterior se nota. Del acta, y de nada más, salen el **CSV** y el **tablero**, para que nunca se contradigan.

Además, en la capa 3, un agente de conciliación lee el acta y redacta un resumen del periodo. Ese agente **no calcula ni modifica cifras**.

## Alcance

**Dentro:**
- Guardar los eventos del sistema en un registro de solo añadir, con cadena de huellas.
- Verificar que la cadena no se haya alterado.
- Derivar el estado actual de cada factura a partir de los eventos.
- Generar el CSV y las cifras del tablero, y comprobar que coincidan.
- Separar los datos por sala de demo.
- El agente de conciliación (capa 3).

**Fuera:**
- Decidir pagar, frenar o escalar (spec `motor-de-reglas`).
- Leer facturas y chatear con el proveedor (spec `extraccion-y-agente-de-entrada`).
- Las pantallas, el despliegue y el refresco automático (spec `paneles-y-despliegue`).
- Anclar la huella en una red pública (queda a futuro).

## Glosario

| Término | Significado |
|---|---|
| Acta | Registro de solo añadir de todos los eventos de una sala. |
| Evento | Una fila del acta. |
| Huella | Resultado de un cálculo (SHA-256) sobre el contenido de una fila y la huella de la anterior. |
| Cadena | La secuencia de filas unidas por sus huellas. |
| Sala | Conjunto de datos de un visitante de la demo, identificado por un código. |
| Estado | Situación actual de una factura: `PAGADA`, `FRENADA`, `PENDIENTE` o `RECHAZADA`. Se calcula, no se guarda. |
| Proyección | Una vista calculada a partir del acta, como el CSV o el tablero. |

## Parámetros por defecto

Valores de demostración, editables.

| Parámetro | Valor | Uso |
|---|---|---|
| `horas_demora_revision` | 24 | Tras este tiempo, un caso escalado sin revisar genera una alerta |
| `horas_purga_sala` | 24 | Después de este tiempo, una sala se puede purgar |
| `repeticiones_patron` | 3 | Veces que se repite una misma causa de escalamiento para avisar |
| `largo_max_motivo` | 500 | Caracteres máximos de un motivo escrito por una persona |

## Requisitos

Notación EARS en español: «CUANDO <evento>, EL ACTA DEBERÁ <respuesta>». También «SI <condición>, ENTONCES …».

### AC1. Registro de solo añadir
**Historia:** como auditor, quiero que lo que quedó escrito no se pueda cambiar.

- **AC1.1** CUANDO se registre un evento, EL ACTA DEBERÁ agregar una fila nueva con un número consecutivo dentro de su sala, sin modificar ninguna fila anterior.
- **AC1.2** EL SISTEMA DEBERÁ impedir que se modifique o se borre una fila del acta: el usuario con el que se conecta la aplicación no tendrá permisos de modificación ni de borrado, y la base de datos rechazará esas operaciones.
- **AC1.3** EL ACTA DEBERÁ aceptar solo estos tipos de evento: `DECISION`, `APROBACION`, `RECHAZO`, `CAMBIO_REGLA`, `INTENTO_RECHAZADO`, `REVISION_CONCILIACION` y `CIERRE_PERIODO`.
- **AC1.4** CUANDO se intente registrar dos veces el mismo evento (misma clave de idempotencia), EL ACTA DEBERÁ devolver la fila existente y no crear otra.
- **AC1.5** EL ACTA DEBERÁ escribir la fila y su huella en una sola transacción. SI la escritura falla, ENTONCES no se escribirá nada y quien llamó recibirá un error, sin que quede un pago registrado.
- **AC1.6** CUANDO dos escrituras lleguen a la vez a la misma sala, EL ACTA DEBERÁ asignarles números distintos y consecutivos, sin repetir ni saltar.

### AC2. Cadena de huellas
**Historia:** como auditor, quiero comprobar que el registro no se alteró.

- **AC2.1** EL ACTA DEBERÁ guardar en cada fila su huella, calculada con SHA-256 sobre la huella de la fila anterior y el contenido canónico de la fila. La primera fila de una sala usará una huella inicial derivada del código de la sala.
- **AC2.2** EL CONTENIDO CANÓNICO DEBERÁ ser un JSON con las claves ordenadas, en UTF-8, con los montos como texto de dos decimales y las fechas en formato ISO 8601 en UTC.
- **AC2.3** CUANDO se pida verificar una sala, EL SISTEMA DEBERÁ recalcular toda la cadena y devolver «correcta» o el número de la primera fila que no coincide.
- **AC2.4** EL SISTEMA DEBERÁ mostrar el resultado de la verificación («cadena verificada: N de N filas») junto al acta.

### AC3. Contenido de cada evento
**Historia:** como persona de finanzas, quiero que cada fila diga qué pasó, por qué y quién lo hizo.

- **AC3.1** Un evento `DECISION` DEBERÁ guardar: factura, beneficiario, monto y moneda originales, monto en moneda base, tasa de cambio usada, decisión, nivel, lista de revisiones, motivo, versión de reglas, canal sugerido y preparador.
- **AC3.2** Un evento `APROBACION` o `RECHAZO` DEBERÁ guardar: actor, rol, motivo obligatorio, el canal elegido si aprueba, y el número de la fila de decisión a la que responde.
- **AC3.3** Un evento `CAMBIO_REGLA` DEBERÁ guardar: parámetros antes y después, si el cambio afloja o restringe, quién lo pidió, quién lo firmó (si aflojó), versión nueva y vigencia.
- **AC3.4** Un evento `INTENTO_RECHAZADO` DEBERÁ guardar qué se intentó, qué regla lo impidió y quién lo intentó.
- **AC3.5** Un evento `REVISION_CONCILIACION` DEBERÁ guardar qué alerta se marcó como revisada y por quién. Un evento `CIERRE_PERIODO` DEBERÁ guardar el periodo, los totales y quién lo cerró.
- **AC3.6** EL ACTA NO DEBERÁ guardar datos personales reales. Los textos libres se limitarán a `largo_max_motivo` caracteres y se guardarán como texto plano.

### AC4. Estado derivado
**Historia:** como persona de finanzas, quiero ver en qué quedó cada factura.

- **AC4.1** EL SISTEMA DEBERÁ calcular el estado de cada factura a partir de su último evento: `PAGADA` (decisión `PAGAR` o aprobación), `FRENADA`, `PENDIENTE` (escalada sin resolver) o `RECHAZADA`. El estado no se guardará aparte.
- **AC4.2** CUANDO una aprobación válida llegue a una factura `PENDIENTE`, EL SISTEMA DEBERÁ pasarla a `PAGADA` (pago de práctica) y registrar el canal elegido.
- **AC4.3** EL SISTEMA DEBERÁ ofrecer al Panel 1 un **estado público** con solo cuatro valores: «recibida», «datos confirmados», «en revisión» y «resuelta». Ese estado NO DEBERÁ incluir motivos, reglas, montos de los umbrales ni nombres de personas.

### AC5. CSV
**Historia:** como persona de finanzas, quiero descargar lo que pasó y abrirlo en una hoja de cálculo.

- **AC5.1** EL SISTEMA DEBERÁ generar los CSV solo a partir del acta, sin otra fuente de datos.
- **AC5.2** EL SISTEMA DEBERÁ ofrecer dos archivos: `facturas.csv` (una fila por factura, con su estado actual) y `eventos.csv` (una fila por cada fila del acta).
- **AC5.3** `facturas.csv` DEBERÁ incluir estas columnas: `factura_id`, `beneficiario`, `monto_original`, `moneda`, `monto_base`, `tasa`, `estado`, `decision_motor`, `nivel`, `aprobador`, `rol_aprobador`, `motivo`, `reglas_fallidas`, `canal_sugerido`, `canal_elegido`, `version_reglas`, `fila_acta`, `huella_corta`, `creado_utc`, `resuelto_utc` y `supuesto`.
- **AC5.4** EL SISTEMA DEBERÁ escribir el CSV en UTF-8 con marca BOM (para que Excel lo lea bien), separado por comas, con el punto como separador decimal y las fechas en ISO 8601.
- **AC5.5** SI una celda de texto empieza con `=`, `+`, `-` o `@`, ENTONCES EL SISTEMA DEBERÁ anteponerle un apóstrofo para que una hoja de cálculo no la ejecute como fórmula.
- **AC5.6** La columna `supuesto` DEBERÁ marcar las filas que usan una tasa de cambio o un canal de ejemplo.
- **AC5.7** PARA la misma acta, EL SISTEMA DEBERÁ generar siempre el mismo CSV, byte por byte.

### AC6. Tablero
**Historia:** como persona de finanzas, quiero ver cuántas facturas hay en cada estado y cuánto se ha gastado.

- **AC6.1** EL SISTEMA DEBERÁ calcular estas cifras: facturas pagadas, frenadas, pendientes de aprobación, esperadas atrasadas (del calendario), gasto del periodo y porcentaje del presupuesto.
- **AC6.2** EL SISTEMA DEBERÁ calcular los totales con código y con `Decimal`, a partir del acta. La IA no calculará ninguna cifra.
- **AC6.3** EL SISTEMA DEBERÁ comprobar que el total del tablero, el del CSV y el recalculado desde el acta coinciden. SI no coinciden, ENTONCES DEBERÁ mostrar un aviso visible y guardar el hecho en el registro de errores.
- **AC6.4** CADA fila del tablero DEBERÁ mostrar la decisión, quién aprueba, el motivo de la última revisión y el canal sugerido.
- **AC6.5** EL SISTEMA DEBERÁ devolver con las cifras la hora de la última actualización, para que el panel muestre cuándo se refrescó.

### AC7. Salas
**Historia:** como evaluador, quiero que mis pruebas no se mezclen con las de otra persona.

- **AC7.1** CADA fila del acta DEBERÁ llevar el código de su sala, y TODAS las consultas DEBERÁN filtrar por sala. Una sala no podrá leer los datos de otra.
- **AC7.2** CADA sala DEBERÁ tener su propia cadena de huellas.
- **AC7.3** CUANDO una persona pida «reiniciar la demo», EL SISTEMA DEBERÁ crear una sala nueva con los datos de ejemplo y dejar la anterior sin tocar.
- **AC7.4** EL SISTEMA DEBERÁ permitir purgar salas con más de `horas_purga_sala` horas solo con un rol de mantenimiento, fuera de la aplicación, y la purga quedará anotada en el registro del servidor.

### AC8. Conciliación (capa 3)
**Historia:** como persona de finanzas, quiero un resumen del periodo y avisos de lo raro, sin que se inventen cifras.

- **AC8.1** EL AGENTE DE CONCILIACIÓN DEBERÁ conectarse con un usuario de solo lectura.
- **AC8.2** EL SISTEMA DEBERÁ entregarle al agente los totales ya calculados y las filas relevantes del acta. Cada cifra de su resumen DEBERÁ citar los números de las filas de donde sale.
- **AC8.3** CUANDO el agente devuelva un resumen, EL SISTEMA DEBERÁ comprobar que cada cifra coincide con los totales entregados. SI alguna no coincide, ENTONCES DEBERÁ descartar el resumen y mostrar el resumen de respaldo.
- **AC8.4** EL SISTEMA DEBERÁ generar estas alertas: factura esperada atrasada, una misma causa de escalamiento repetida `repeticiones_patron` veces, un caso escalado sin revisar por más de `horas_demora_revision`, y cadena no verificada.
- **AC8.5** SI el modelo falla o no hay clave, ENTONCES EL SISTEMA DEBERÁ mostrar un **resumen de respaldo**, armado con una plantilla y los totales, sin IA.
- **AC8.6** Las alertas serán sugerencias. CUANDO una persona marque una como revisada, EL SISTEMA DEBERÁ registrar un evento `REVISION_CONCILIACION`.
- **AC8.7** EL SISTEMA DEBERÁ tratar los textos que escribieron personas (motivos) como datos y nunca como instrucciones para el agente.

### AC9. Calidad
- **AC9.1** Cada criterio de esta spec DEBERÁ tener al menos una prueba automática.
- **AC9.2** Una prueba DEBERÁ comprobar que modificar o borrar una fila falla.
- **AC9.3** Una prueba DEBERÁ comprobar que alterar una fila rompe la verificación y señala cuál fue.
- **AC9.4** Una prueba DEBERÁ comprobar que con las 20 facturas de prueba el tablero, el CSV y el acta suman lo mismo.
- **AC9.5** Una prueba DEBERÁ comprobar que dos escrituras simultáneas no repiten ni saltan números.
- **AC9.6** Una prueba DEBERÁ comprobar que una celda con fórmula queda neutralizada en el CSV.
- **AC9.7** Una prueba DEBERÁ comprobar que una sala no puede leer a otra.
- **AC9.8** Una prueba DEBERÁ comprobar que repetir un evento con la misma clave no crea una fila nueva.
- **AC9.9** Escribir un evento NO DEBERÍA tardar más de 200 ms, y generar los CSV de 1.000 filas, no más de 1 s.

## Decisiones abiertas

| # | Pregunta | Propuesta por defecto |
|---|---|---|
| DA1 | ¿Una fila por evento o solo por decisión final? | Por evento: así se ve toda la historia de cada factura. |
| DA2 | ¿Una cadena por sala o una global? | Por sala, porque cada sala es independiente. |
| DA3 | ¿Separador del CSV? | Coma con BOM. Ofrecer una descarga alternativa con punto y coma para Excel en español. |
| DA4 | ¿Reiniciar la demo borra la sala anterior? | No: crea una nueva y la anterior se purga a las 24 h. |
| DA5 | ¿Publicar la huella en una red pública? | A futuro. No entra en esta spec. |
