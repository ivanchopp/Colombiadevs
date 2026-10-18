# Requisitos: paneles y despliegue

Estado: **borrador para revisión del equipo**.
Base: «Ruta de una factura» (`docs/Ruta-de-una-factura.pdf`, sección «Los dos paneles de la demo» y sus maquetas) y la spec `specs/acta-y-csv/`.

## Resumen

La demo tiene dos pantallas que comparten una *sala*: el **Panel 1** (proveedor, abierto) y el **Panel 2** (finanzas, con rol). Los dos **solo muestran** lo que sale del acta y del motor de reglas. Ninguna pantalla calcula cifras ni decide pagos. Esta spec cubre los **tableros** (Panel 2) y el portal del proveedor (Panel 1); el despliegue en Railway queda como tarea final.

## Alcance

**Dentro:** Panel 1 (portal, estado público), Panel 2 (tablero, cola de aprobación, detalle, calendario, acta, descarga de CSV), sala por enlace, selector de rol, refresco automático.

**Fuera (otras specs):** lectura de facturas y chat con el proveedor (`extraccion-y-agente-de-entrada`), chat de reglas en lenguaje natural y resumen con IA (capa 3), reglas de decisión (`motor-de-reglas`).

## Parámetros por defecto (supuestos)

| Parámetro | Valor |
|---|---|
| `segundos_refresco` | 5 |
| `facturas_max_por_sala` | 5 (se cambia con la variable `FACTURAS_MAX`) |
| Roles de demostración | `PERSONA`, `SENIOR` |

## Requisitos

### PP1. Sala
- **PP1.1** CUANDO se abra cualquier panel sin código de sala, EL SISTEMA DEBERÁ crear una sala nueva con datos de ejemplo y poner su código en el enlace (`?sala=`).
- **PP1.2** CUANDO el enlace traiga un código de sala válido, EL SISTEMA DEBERÁ mostrar solo los datos de esa sala (AC7.1).
- **PP1.3** CUANDO el enlace traiga un código inexistente o con formato inválido, EL SISTEMA DEBERÁ crear una sala nueva y avisarlo.
- **PP1.4** EL BOTÓN «Abrir panel de finanzas» DEBERÁ llevar el código de la sala al Panel 2.

### PP2. Panel 1 (proveedor)
- **PP2.1** EL PANEL 1 NO DEBERÁ mostrar reglas, umbrales, motivos internos, nombres de personas ni montos de límites (AC4.3).
- **PP2.2** EL PANEL 1 DEBERÁ mostrar por factura solo el estado público: «recibida», «datos confirmados», «en revisión» o «resuelta».
- **PP2.3** EL PANEL 1 DEBERÁ indicar que los datos son ficticios y cuántas facturas se han usado de `facturas_max_por_sala`. EL aviso NO DEBERÁ llamar «demo» a los datos ficticios, para no confundirse con el modo demo de la IA (EA8.3): dice «Datos ficticios, solo para práctica».
- **PP2.4** EL PANEL 1 NO DEBERÁ ofrecer botones que registren una factura sin que el sistema la lea: la única entrada es subir un archivo. El sistema DEBERÁ leer el archivo y dejar que el motor de reglas decida si es normal, repetida, de beneficiario nuevo o con una orden escondida; nada en la pantalla elige ese resultado.
- **PP2.5** EL PANEL 1 DEBERÁ ofrecer cuatro archivos de muestra ficticios para descargar y volver a subir, con un nombre neutro (el proveedor y el número de factura), sin decir qué caso es cada uno ni qué regla activa (PP2.1). La guía de qué caso muestra cada archivo queda en el `README.md`.
- **PP2.6** CUANDO el proveedor envíe una factura, EL PANEL 1 DEBERÁ vaciar el selector de archivos (el archivo enviado no queda cargado ni se puede reenviar por error) y mostrar el chat de **esa** factura, sin texto escrito de otra. EL cuadro de respuesta DEBERÁ aparecer solo mientras la factura espera aclaraciones.
- **PP2.7** EL Panel 1 DEBERÁ llamarse **«Envía facturas»** en el menú lateral y en su título de página (antes «Panel 1 · Portal del proveedor»). Sigue siendo el portal abierto de PP2.1.

### PP3. Roles (Panel 2)
- **PP3.1** EL PANEL 2 DEBERÁ entrar por defecto como **`PERSONA`** (persona de finanzas) en cada sala nueva, sin pedir elegir, y recordar el rol que se elija al pasar de una página a otra. Es un selector de demostración, no un inicio de sesión. *(Antes pedía elegir un rol antes de mostrar datos.)*
- **PP3.2** EL PANEL 2 DEBERÁ mostrar el rol activo en todas las páginas.
- **PP3.3** CUANDO haya aprobaciones pendientes que se pueden aprobar, EL SELECTOR de rol DEBERÁ mostrar un **punto rojo con el número** sobre el rol al que le corresponde aprobarlas: las de nivel `PERSONA` sobre «Persona de finanzas» y las de nivel `SENIOR` sobre «Senior de finanzas». SIN pendientes, ningún punto. NO DEBERÁ contar las facturas de ficha inválida (PP5.7), que solo se pueden rechazar.
- **PP3.4** EL PANEL 2 DEBERÁ mostrar en el menú lateral, bajo el código de sala, un aviso «🔴 N aprobación(es) pendiente(s) en la cola» con las que el rol activo puede ver (PP5.1), solo si N > 0. El Panel 1 NO DEBERÁ mostrar este aviso ni ningún conteo (PP2.1).
- **PP3.5** LOS puntos se calculan desde el acta (el estado de cada factura), no se guardan; se actualizan cada vez que se vuelve a cargar la página.

### PP4. Tablero
- **PP4.1** EL TABLERO DEBERÁ mostrar las cifras de AC6.1 (pagadas, frenadas, pendientes, esperadas atrasadas, gasto y porcentaje del presupuesto), tal como las entrega `acta/tablero.py`.
- **PP4.2** (Para una ficha inválida, el monto se muestra como «sin leer».) CADA fila DEBERÁ mostrar factura, proveedor, monto, decisión, quién aprueba, motivo y canal sugerido (AC6.4).
- **PP4.3** EL TABLERO DEBERÁ refrescarse cada `segundos_refresco` y mostrar la hora de la última actualización (AC6.5).
- **PP4.4** SI el tablero, el CSV y el acta no coinciden (AC6.3), ENTONCES EL TABLERO DEBERÁ mostrar un aviso visible.
- **PP4.5** EL TABLERO DEBERÁ ofrecer la descarga de `facturas.csv` y `eventos.csv` (AC5).
- **PP4.6** EL TABLERO DEBERÁ marcar como «supuesto» las tasas, canales y costos de ejemplo, y decir cuál es la moneda base (la configurada en `reglas.yaml`, hoy USD) sin suponerla (R5.6).

### PP5. Cola de aprobación
- **PP5.1** CADA rol DEBERÁ ver solo los casos de su nivel: `PERSONA` los de nivel persona; `SENIOR` los de nivel senior (y puede ver los de persona).
- **PP5.2** PARA aprobar o rechazar, EL SISTEMA DEBERÁ exigir un motivo no vacío, de máximo `largo_max_motivo` caracteres (AC3.2, AC3.6).
- **PP5.3** SI el rol no alcanza el nivel exigido, ENTONCES EL SISTEMA DEBERÁ rechazar la acción y registrar un `INTENTO_RECHAZADO` (AC3.4).
- **PP5.4** SI quien aprueba es el preparador del caso, ENTONCES EL SISTEMA DEBERÁ rechazar la acción (separación de funciones, R8.2).
- **PP5.5** AL aprobar, EL SISTEMA DEBERÁ permitir elegir el canal de pago y registrarlo en el acta. La aprobación es un pago de práctica: no mueve dinero.
- **PP5.6** LA interfaz NUNCA DEBERÁ mostrar un pago como hecho si la escritura en el acta falló (AC1.5).
- **PP5.7** SI la factura tiene la ficha inválida (R8.6), ENTONCES la cola DEBERÁ mostrarla con su motivo, NO DEBERÁ ofrecer el botón de aprobar y EL SISTEMA DEBERÁ rechazar cualquier intento de aprobarla, registrando un `INTENTO_RECHAZADO`. Solo se podrá rechazar.

### PP6. Detalle, calendario y acta
- **PP6.1** EL DETALLE de una factura DEBERÁ mostrar la ficha, la lista de revisiones (OK, FALLA, AVISO), el resultado, la versión de reglas y el número de fila del acta.
- **PP6.2** EL CALENDARIO DEBERÁ mostrar las obligaciones del mes con su estado: «llegó», «pendiente», «atrasada» e «inesperada».
- **PP6.3** LA página del acta DEBERÁ ser de solo lectura y mostrar el resultado de la verificación de la cadena (AC2.4).

### PP7. Calidad
- **PP7.1** Las pantallas NO DEBERÁN contener lógica de decisión ni cálculos de dinero: llaman a `acta/` y `engine/`.
- **PP7.2** Cada criterio de PP1, PP2 y PP5 DEBERÁ tener una prueba automática sobre las funciones de apoyo (`app/apoyo.py`), y las páginas se prueban con `streamlit.testing.v1.AppTest`.
- **PP7.3** EL texto escrito por personas (motivos, nombres) DEBERÁ mostrarse como texto plano, nunca como HTML.

### PP8. Reglas (entregable del reto)
**Historia:** como persona de finanzas, quiero ver y cambiar las reglas de pago desde una pantalla, sin pedirle ayuda a ingeniería.

- **PP8.1** EL PANEL 2 DEBERÁ tener una página «Reglas» que muestre los parámetros vigentes de la sala, su versión y el techo duro (de solo lectura, R9.5).
- **PP8.2** LA página DEBERÁ permitir editar con un formulario: `autopago_max`, `persona_max`, `limite_periodo_beneficiario`, `presupuesto_periodo`, `tolerancia_ok`, `tolerancia_frenar` y `ventana_dias`.
- **PP8.3** ANTES de confirmar, LA página DEBERÁ mostrar qué cambia, si el cambio afloja o restringe, y qué facturas de la sala cambiarían de decisión (vista previa, R9.6), sin escribir nada.
- **PP8.4** SI el cambio afloja una regla (R9.4), ENTONCES solo el rol `SENIOR` podrá confirmarlo. SI lo intenta `PERSONA`, ENTONCES EL SISTEMA DEBERÁ rechazarlo y registrar un `INTENTO_RECHAZADO`.
- **PP8.5** SI un umbral de monto supera el techo duro, o los valores no son coherentes (`autopago_max` ≤ `persona_max`, `tolerancia_ok` ≤ `tolerancia_frenar`, valores positivos), ENTONCES EL SISTEMA DEBERÁ rechazar el cambio con una explicación (R9.5).
- **PP8.6** PARA confirmar, EL SISTEMA DEBERÁ exigir un motivo y registrar un evento `CAMBIO_REGLA` con los valores antes y después, si afloja, quién lo pidió, quién lo firmó y la versión nueva (AC3.3).
- **PP8.7** UN cambio confirmado DEBERÁ aplicarse solo a las facturas que se decidan después, y solo en esa sala. Las decisiones ya registradas no cambian.

### PP9. Órdenes de compra (OC6)
- **PP9.1** (OC6.1) EL PANEL 2 DEBERÁ tener una página «Órdenes de compra» con cada orden: número, proveedor, artículo, total en la moneda de la orden, estado («abierta» o «facturada») y, si está facturada, la factura que la usó con su estado. Las cifras de arriba (abiertas y facturadas) salen del mismo cálculo que el motor (OC5), no de la pantalla.
- **PP9.2** LA página DEBERÁ decir que las órdenes son de ejemplo («supuesto») y mostrar una orden marcada «no coincide con el proveedor» con esa advertencia.
- **PP9.3** (OC6.2) EL detalle de una factura DEBERÁ mostrar, si cita una orden, su número, proveedor, total y estado, y el resultado de la revisión de la orden (OC4). SI cita una orden que no existe, ENTONCES DEBERÁ decir «orden inexistente»; NUNCA inventar datos.
- **PP9.4** (OC6.3) EL PANEL 1 NO DEBERÁ mostrar órdenes, montos autorizados ni si una orden existe.
- **PP9.5** LAS funciones de apoyo (`app/apoyo.py`) DEBERÁN armar estas vistas sin lógica de decisión (PP7.1) y el texto de proveedores y artículos se muestra como texto plano (PP7.3).

## Decisiones abiertas

| # | Pregunta | Propuesta por defecto |
|---|---|---|
| DP1 | ¿Panel 1 y Panel 2 en una sola app o en dos? | Una sola app Streamlit con `pages/` (menos despliegue) |
| DP2 | ¿La cola del senior incluye los casos de persona? | Sí, puede verlos pero la persona no ve los del senior |
| DP3 | ¿Qué hace el Panel 1 mientras no exista el agente de entrada? | Resuelta: el agente de entrada ya existe (modo demo sin clave) |

## Despliegue (PD)

### PD1. Railway
- **PD1.1** EL SISTEMA DEBERÁ arrancar con un solo comando, escuchando en `0.0.0.0` y en el puerto de la variable `PORT`.
- **PD1.2** EL SISTEMA DEBERÁ responder a una comprobación de salud en `/_stcore/health`.
- **PD1.3** LA base del acta DEBERÁ guardarse en el volumen de Railway cuando exista (`RAILWAY_VOLUME_MOUNT_PATH`), y en `ACTA_DB` si se define; si no hay ninguno, en `data/` (se pierde al reiniciar).
- **PD1.4** LAS claves (`ANTHROPIC_API_KEY`) NO DEBERÁN estar en el repositorio: solo nombres en `.env.example`.
- **PD1.5** SI la variable `FECHA_DEMO` existe, ENTONCES EL SISTEMA DEBERÁ usarla como «hoy» para el calendario y las reglas, para que la demo no dependa del día en que se pruebe.
- **PD1.6** EL SISTEMA NO DEBERÁ fallar si dos visitantes escriben a la vez: la base usa modo WAL y espera por el bloqueo.

## Decisión de despliegue (17 oct)

Para la entrega se usa **SQLite sobre un volumen de Railway**, con una sola réplica. Es lo más simple y lo que se puede probar hoy. **PostgreSQL con roles y permisos (AC1.2) queda pendiente** (P13): hasta entonces la inmutabilidad del acta la garantizan los triggers y la cadena de huellas, no los permisos del usuario de la base.
