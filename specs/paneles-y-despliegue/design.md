# Diseño: paneles y despliegue

Estado: **borrador para revisión del equipo**. Requisitos: `requirements.md`. Diseño general: `docs/Ruta-de-una-factura.pdf`.

## Principios

1. **Las pantallas solo muestran.** Todo cálculo vive en `acta/` (cifras, estado, CSV) y toda decisión en `engine/`.
2. **Una fuente de verdad:** el acta. Las pantallas leen proyecciones, nunca tablas propias.
3. **Una app, dos paneles.** `app/Panel_1_Proveedor.py` es la entrada; el Panel 2 vive en `app/pages/`.
4. **Texto de personas = texto plano** (nada de `unsafe_allow_html` con datos de usuario).

## Estructura

```
app/
├─ Panel_1_Proveedor.py     # portal abierto: estado público, facturas de ejemplo
├─ comun.py                 # sala por enlace, conexión al acta, selector de rol, formato
├─ apoyo.py                 # funciones puras: cola por rol, validar aprobación, formato de montos
└─ pages/
   ├─ 1_Tablero.py          # cifras, tabla, CSV, aviso de consistencia (refresco con st.fragment)
   ├─ 2_Cola_de_aprobacion.py
   ├─ 3_Calendario.py
   └─ 4_Acta.py             # solo lectura + verificación de cadena
acta/                       # ver specs/acta-y-csv/design.md
data/demo_semilla.py        # eventos de ejemplo de las maquetas (sustituir por el motor)
```

## Flujo de datos

```mermaid
flowchart LR
    A[(acta)] --> E[estado.py]
    E --> T[tablero.py cifras]
    E --> C[exportar_csv.py]
    T --> P2[Panel 2]
    C --> P2
    E --> P1[Panel 1: estado público]
    P2 -->|aprobar o rechazar| G[apoyo.validar_aprobacion] --> W[escribir_evento] --> A
```

## Sala y rol

- `comun.obtener_sala()` lee `st.query_params["sala"]`; si falta o es inválida, crea una sala con `salas.crear()` (carga la semilla) y actualiza el enlace.
- El rol vive en `st.session_state["rol"]`; `comun.exigir_rol()` detiene la página si no hay rol.

## Cola y aprobaciones (provisional)

`apoyo.validar_aprobacion(rol, nivel, motivo, actor, preparador)` aplica PP5.2 a PP5.4. Cuando exista `engine/guardarrail.py` (T9), esta función se sustituye por la suya y la pantalla no cambia.

## Refresco

`st.fragment(run_every=segundos_refresco)` solo en el tablero. Hay que verificar que la versión de Streamlit fijada lo soporte (pendiente P4).

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Se muestra como pagada una factura cuya escritura falló | Mostrar el éxito solo después de que `escribir_evento` devuelva la fila (PP5.6) |
| El Panel 1 filtra reglas o motivos | Estado público con lista cerrada y prueba específica (PP2.1) |
| Texto con HTML en un motivo | Mostrar siempre con `st.text` / `st.write` sin HTML (PP7.3) |

## Página de reglas (PP8)

- **Dónde vive un cambio:** en el acta de la sala, como evento `CAMBIO_REGLA` (tipo ya permitido por AC1.3). `reglas.yaml` no se toca, así cada visitante cambia sus reglas sin afectar a los demás y el cambio queda en la cadena de huellas.
- **Reglas de una sala:** `engine.reglas_io.reglas_de_sala(base, filas)` toma las reglas vigentes de `reglas.yaml` y les aplica el último `CAMBIO_REGLA` de la sala. La versión queda como `<versión base>.s<n>` (por ejemplo `v12.s1`) y aparece en cada decisión. La usan los paneles y el agente de entrada al decidir.
- **Afloja o restringe:** `cambios_que_aflojan(antes, después)`. Afloja si sube un umbral de monto, el presupuesto, una tolerancia o la ventana de días.
- **Validación:** `validar_cambio` exige valores positivos, `autopago_max` ≤ `persona_max`, `tolerancia_ok` ≤ `tolerancia_frenar` ≤ 1 y que ningún umbral de monto pase el techo duro. El techo duro no es editable.
- **Vista previa:** `engine.simular.simular(filas, ctx, antes, después)` vuelve a evaluar la ficha guardada de cada decisión con las dos versiones y devuelve las que cambian. No escribe nada.
- **Confirmar:** `app.apoyo.cambiar_reglas` valida rol, motivo y coherencia, y escribe el evento. Si un rol `PERSONA` intenta aflojar, se registra `INTENTO_RECHAZADO`.
- shortcut: el cambio se aplica sobre la versión base vigente hoy; si `reglas.yaml` cambia de versión, la sala conserva sus parámetros cambiados. Basta para la demo.
