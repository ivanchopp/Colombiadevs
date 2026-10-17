CREATE TABLE IF NOT EXISTS acta (
  sala_id          TEXT    NOT NULL,
  num              INTEGER NOT NULL,
  tipo             TEXT    NOT NULL CHECK (tipo IN (
                     'DECISION','APROBACION','RECHAZO','CAMBIO_REGLA',
                     'INTENTO_RECHAZADO','REVISION_CONCILIACION','CIERRE_PERIODO')),
  factura_id       TEXT,
  payload          TEXT    NOT NULL,
  actor            TEXT    NOT NULL,
  clave_idem       TEXT    NOT NULL,
  huella_anterior  TEXT    NOT NULL,
  huella           TEXT    NOT NULL,
  creado_en        TEXT    NOT NULL,
  PRIMARY KEY (sala_id, num),
  UNIQUE (sala_id, clave_idem)
);

CREATE TRIGGER IF NOT EXISTS acta_no_modifica BEFORE UPDATE ON acta
BEGIN SELECT RAISE(ABORT, 'el acta es de solo añadir'); END;

CREATE TRIGGER IF NOT EXISTS acta_no_borra BEFORE DELETE ON acta
BEGIN SELECT RAISE(ABORT, 'el acta es de solo añadir'); END;
