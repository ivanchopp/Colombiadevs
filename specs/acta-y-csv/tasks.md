# Tareas: acta y CSV

Estado: **borrador para revisión del equipo**.
Requisitos: `requirements.md` · Diseño: `design.md`.

Las horas son **estimaciones mías**, para planear. Una tarea está lista cuando las pruebas de sus criterios pasan.

Dueños sugeridos: **A** motor y pruebas · **B** agentes · **C** pantallas · **D** datos, evaluación y pitch.
Como esta spec tiene bastante trabajo de infraestructura, se propone **C como responsable**, con A en la conexión con el motor y D en el CSV y las pruebas.

## Prioridad

| Capa | Qué incluye | Hasta cuándo |
|---|---|---|
| **Núcleo** | AT1 a AT9: tabla de solo añadir, huellas, escritura, estado, CSV, cifras y salas | Sábado 18:00 |
| **Capa 3** | AT10: agente de conciliación y resumen de respaldo | Solo si sobra tiempo |
| **A futuro** | Anclar la huella en una red pública | No se construye |

### Versión mínima si falta tiempo
Si a las 14:00 el núcleo va atrasado, se puede reducir así, sin perder los criterios de seguridad:
- Usar **solo SQLite** (con los triggers) en vez de PostgreSQL. Los datos se reinician con el despliegue.
- Generar **solo `facturas.csv`**, sin `eventos.csv`.
- Dejar la purga de salas (AC7.4) como un script manual.
- Mantener sin recortar: solo añadir (AC1.2), huellas y verificación (AC2), neutralización de fórmulas (AC5.5) y estado público (AC4.3).

## Dependencias

```mermaid
flowchart TD
    M1[Motor T1: modelos] --> AT3
    AT1[AT1 Tabla, permisos y almacén] --> AT2[AT2 Huellas y verificación]
    AT1 --> AT3[AT3 Escribir eventos]
    AT2 --> AT3
    AT3 --> AT4[AT4 Estado derivado]
    AT4 --> AT5[AT5 CSV]
    AT4 --> AT6[AT6 Cifras y consistencia]
    AT5 --> AT6
    AT1 --> AT7[AT7 Salas]
    AT3 --> AT8[AT8 Conexión con el motor]
    AT8 --> AT9[AT9 Pruebas de conjunto]
    AT6 --> AT9
    AT6 --> AT10[AT10 Conciliación]
```

## Tareas

### AT1. Tabla, permisos y almacén
- **Dueño:** C · **Estimación:** 1,5 h · **Capa:** núcleo
- Crear `esquema_postgres.sql` y `esquema_sqlite.sql` (tabla, restricción única, triggers y roles), y `almacen.py` con la interfaz y las dos implementaciones.
- **Cubre:** AC1.1, AC1.2, AC1.6 (la restricción), AC7.1 (el filtro por sala)
- **Listo cuando:** `UPDATE` y `DELETE` desde el usuario de la aplicación fallan en las dos bases.

### AT2. Huellas y verificación
- **Dueño:** C · **Estimación:** 1 h · **Capa:** núcleo
- `huella.py` (contenido canónico, huella inicial) y `verificar.py`.
- **Cubre:** AC2.1 a AC2.4
- **Listo cuando:** una huella de ejemplo con valores fijos da siempre el mismo resultado, y alterar una fila hace que la verificación señale cuál es.

### AT3. Escribir eventos
- **Dueño:** C (con A para los payloads) · **Estimación:** 1 h · **Capa:** núcleo
- `eventos.py` (los 7 tipos con Pydantic) y `escribir.py` (transacción, bloqueo por sala, idempotencia).
- **Cubre:** AC1.3 a AC1.6, AC3.1 a AC3.6
- **Listo cuando:** escrituras simultáneas no repiten ni saltan números, y repetir un evento no crea otra fila.

### AT4. Estado derivado
- **Dueño:** C · **Estimación:** 0,75 h · **Capa:** núcleo
- `estado.py`: estado por factura y estado público.
- **Cubre:** AC4.1 a AC4.3
- **Listo cuando:** el estado público nunca contiene motivos, reglas ni montos de umbrales.

### AT5. CSV
- **Dueño:** D (apoyo C) · **Estimación:** 1 h · **Capa:** núcleo
- `exportar_csv.py`: `facturas.csv` y `eventos.csv`, BOM, neutralización de fórmulas, columna `supuesto` y variante con punto y coma.
- **Cubre:** AC5.1 a AC5.7
- **Listo cuando:** el CSV abre bien en una hoja de cálculo y una celda `=1+1` sale como texto.

### AT6. Cifras y consistencia
- **Dueño:** C · **Estimación:** 1 h · **Capa:** núcleo
- `tablero.py`: cifras, hora de actualización y comprobación de que tablero, CSV y acta coinciden.
- **Cubre:** AC6.1 a AC6.5
- **Listo cuando:** con los 20 casos las tres cifras coinciden, y forzar una diferencia dispara el aviso.

### AT7. Salas
- **Dueño:** C · **Estimación:** 0,75 h · **Capa:** núcleo
- `salas.py`: crear, reiniciar (sala nueva con datos de ejemplo) y purgar (script de mantenimiento).
- **Cubre:** AC7.1 a AC7.4
- **Listo cuando:** una sala no puede leer otra y reiniciar deja intacta la anterior.

### AT8. Conexión con el motor de reglas
- **Dueño:** A con C · **Estimación:** 0,75 h · **Capa:** núcleo
- Conectar `registrar_decision` y las aprobaciones con `escribir_evento`. Es la tarea T15 de la spec del motor.
- **Listo cuando:** una decisión aprobada queda en el acta con versión de reglas, motivo, revisiones y canal, y si la escritura falla, el motor no la da por hecha.

### AT9. Pruebas de conjunto
- **Dueño:** D con C · **Estimación:** 1,25 h · **Capa:** núcleo
- Pruebas AC9.1 a AC9.9 sobre las 20 facturas, y el script que alimenta `eval.py` con la verificación de la cadena.
- **Listo cuando:** pasan en SQLite y, si hay base disponible, en PostgreSQL.

### AT10. Conciliación
- **Dueño:** B · **Estimación:** 2 h · **Capa:** capa 3
- `conciliacion.py`: alertas con código, redacción con IA, validación de cifras y resumen de respaldo, con el usuario de solo lectura.
- **Cubre:** AC8.1 a AC8.7
- **Listo cuando:** un borrador con una cifra inventada se descarta, y sin clave de API sale el resumen de respaldo.

## Trazabilidad

| Requisito | Tarea | Archivo de pruebas |
|---|---|---|
| AC1.1, AC1.2 | AT1 | `tests/test_acta_inmutable.py` |
| AC1.3 a AC1.6 | AT3 | `tests/test_acta_escribir.py` |
| AC2.* | AT2 | `tests/test_acta_huellas.py` |
| AC3.* | AT3 | `tests/test_acta_eventos.py` |
| AC4.* | AT4 | `tests/test_acta_estado.py` |
| AC5.* | AT5 | `tests/test_csv.py` |
| AC6.* | AT6 | `tests/test_tablero.py` |
| AC7.* | AT7 | `tests/test_salas.py` |
| AC8.* | AT10 | `tests/test_conciliacion.py` |
| AC9.1 | Todas | Una prueba por criterio |
| AC9.2 a AC9.9 | AT9 | Pruebas de conjunto en `tests/` |

## Orden sugerido

1. **Ahora a 12:30:** AT1 y AT2, con los modelos del motor (T1) ya disponibles.
2. **12:30 a 14:00:** AT3 y AT4.
3. **14:00 a 16:00:** AT5, AT6 y AT7, junto con las pantallas.
4. **16:00 a 18:00:** AT8 y AT9. Las cifras alimentan el control de las 18:00.
5. **Después del control:** AT10, solo si sobra tiempo.
