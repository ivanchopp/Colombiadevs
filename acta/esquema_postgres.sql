-- Acta de solo añadir (spec acta-y-csv, AC1). Versión PostgreSQL de Railway.
-- SIN PROBAR todavía (tarea AT1). Crear antes los roles usuario_app, usuario_lectura y usuario_mantenimiento.
CREATE TABLE IF NOT EXISTS acta (
  sala_id          text        NOT NULL,
  num              integer     NOT NULL,
  tipo             text        NOT NULL CHECK (tipo IN (
                     'DECISION','APROBACION','RECHAZO','CAMBIO_REGLA',
                     'INTENTO_RECHAZADO','REVISION_CONCILIACION','CIERRE_PERIODO')),
  factura_id       text,
  payload          jsonb       NOT NULL,
  actor            text        NOT NULL,
  clave_idem       text        NOT NULL,
  huella_anterior  char(64)   NOT NULL,
  huella           char(64)   NOT NULL,
  creado_en        timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (sala_id, num),
  UNIQUE (sala_id, clave_idem)
);

-- La aplicación solo puede leer y añadir; el agente de conciliación solo puede leer.
REVOKE UPDATE, DELETE, TRUNCATE ON acta FROM usuario_app;
GRANT  SELECT, INSERT           ON acta TO usuario_app;
GRANT  SELECT                   ON acta TO usuario_lectura;

-- Segunda barrera: aunque alguien tenga permisos, la fila no se toca.
CREATE OR REPLACE FUNCTION bloquear_cambios() RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION 'el acta es de solo añadir';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS acta_inmutable ON acta;
CREATE TRIGGER acta_inmutable BEFORE UPDATE OR DELETE ON acta
  FOR EACH ROW EXECUTE FUNCTION bloquear_cambios();
