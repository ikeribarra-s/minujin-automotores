-- ============================================================
--  Automotora — Schema PostgreSQL
-- ============================================================

CREATE TYPE estado_vehiculo   AS ENUM ('disponible', 'reservado', 'vendido');
CREATE TYPE tipo_vehiculo     AS ENUM ('usado', 'cero_km');
CREATE TYPE procedencia       AS ENUM ('compra', 'permuta', 'consignacion');
CREATE TYPE forma_pago_venta  AS ENUM ('contado', 'financiado', 'permuta', 'mixto');
CREATE TYPE concepto_cobro    AS ENUM ('sena', 'saldo', 'cuota', 'otro');
CREATE TYPE forma_pago_cobro  AS ENUM ('efectivo', 'transferencia', 'cheque', 'tarjeta');
CREATE TYPE estado_cheque     AS ENUM ('pendiente', 'cobrado', 'rechazado', 'depositado');

-- ------------------------------------------------------------
--  VEHICULO
-- ------------------------------------------------------------
CREATE TABLE vehiculo (
    id               SERIAL PRIMARY KEY,
    marca            VARCHAR(60)    NOT NULL,
    modelo           VARCHAR(80)    NOT NULL,
    version          VARCHAR(80),
    anio             SMALLINT       NOT NULL CHECK (anio BETWEEN 1950 AND 2100),
    color            VARCHAR(40),
    kilometraje      INTEGER        DEFAULT 0 CHECK (kilometraje >= 0),
    tipo             tipo_vehiculo  NOT NULL DEFAULT 'usado',
    numero_motor     VARCHAR(60),
    numero_chasis    VARCHAR(60),
    patente          VARCHAR(20),
    precio_compra    NUMERIC(14,2),
    precio_venta     NUMERIC(14,2),
    estado           estado_vehiculo NOT NULL DEFAULT 'disponible',
    procedencia      procedencia    NOT NULL DEFAULT 'compra',
    observaciones    TEXT,
    fecha_ingreso    DATE           NOT NULL DEFAULT CURRENT_DATE,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
--  CLIENTE
-- ------------------------------------------------------------
CREATE TABLE cliente (
    id               SERIAL PRIMARY KEY,
    nombre           VARCHAR(80)    NOT NULL,
    apellido         VARCHAR(80)    NOT NULL,
    dni              VARCHAR(20)    UNIQUE,
    telefono         VARCHAR(40),
    email            VARCHAR(120),
    direccion        TEXT,
    fecha_alta       DATE           NOT NULL DEFAULT CURRENT_DATE,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
--  VENTA
-- ------------------------------------------------------------
CREATE TABLE venta (
    id               SERIAL PRIMARY KEY,
    vehiculo_id      INTEGER        NOT NULL REFERENCES vehiculo(id),
    cliente_id       INTEGER        NOT NULL REFERENCES cliente(id),
    precio_final     NUMERIC(14,2)  NOT NULL CHECK (precio_final > 0),
    forma_pago       forma_pago_venta NOT NULL DEFAULT 'contado',
    fecha_venta      DATE           NOT NULL DEFAULT CURRENT_DATE,
    observaciones    TEXT,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- Un vehículo solo puede tener una venta activa
CREATE UNIQUE INDEX venta_vehiculo_unico ON venta(vehiculo_id);

-- ------------------------------------------------------------
--  COBRO
-- ------------------------------------------------------------
CREATE TABLE cobro (
    id               SERIAL PRIMARY KEY,
    venta_id         INTEGER        NOT NULL REFERENCES venta(id),
    cliente_id       INTEGER        NOT NULL REFERENCES cliente(id),
    concepto         concepto_cobro NOT NULL DEFAULT 'saldo',
    monto            NUMERIC(14,2)  NOT NULL CHECK (monto > 0),
    forma_pago       forma_pago_cobro NOT NULL DEFAULT 'efectivo',
    fecha            DATE           NOT NULL DEFAULT CURRENT_DATE,
    observaciones    TEXT,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
--  CHEQUE
-- ------------------------------------------------------------
CREATE TABLE cheque (
    id               SERIAL PRIMARY KEY,
    cobro_id         INTEGER        NOT NULL REFERENCES cobro(id),
    numero           VARCHAR(20)    NOT NULL,
    banco            VARCHAR(80)    NOT NULL,
    titular          VARCHAR(160),
    monto            NUMERIC(14,2)  NOT NULL CHECK (monto > 0),
    fecha_emision    DATE,
    fecha_cobro      DATE           NOT NULL,
    estado           estado_cheque  NOT NULL DEFAULT 'pendiente',
    observaciones    TEXT,
    created_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
--  PERMUTA  (vehículo recibido como parte de pago)
-- ------------------------------------------------------------
CREATE TABLE permuta (
    id                    SERIAL PRIMARY KEY,
    venta_id              INTEGER        NOT NULL REFERENCES venta(id),
    vehiculo_recibido_id  INTEGER        NOT NULL REFERENCES vehiculo(id),
    valor_tasacion        NUMERIC(14,2)  NOT NULL CHECK (valor_tasacion >= 0),
    observaciones         TEXT,
    created_at            TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
--  TRIGGER: updated_at automático
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_vehiculo_updated  BEFORE UPDATE ON vehiculo  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_cliente_updated   BEFORE UPDATE ON cliente   FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_venta_updated     BEFORE UPDATE ON venta     FOR EACH ROW EXECUTE FUNCTION set_updated_at();
CREATE TRIGGER trg_cheque_updated    BEFORE UPDATE ON cheque    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ------------------------------------------------------------
--  TRIGGER: marcar vehículo como vendido al registrar venta
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION marcar_vehiculo_vendido()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE vehiculo SET estado = 'vendido' WHERE id = NEW.vehiculo_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_venta_insert
    AFTER INSERT ON venta
    FOR EACH ROW EXECUTE FUNCTION marcar_vehiculo_vendido();

-- ------------------------------------------------------------
--  ÍNDICES útiles
-- ------------------------------------------------------------
CREATE INDEX idx_vehiculo_estado    ON vehiculo(estado);
CREATE INDEX idx_vehiculo_marca     ON vehiculo(marca);
CREATE INDEX idx_cliente_dni        ON cliente(dni);
CREATE INDEX idx_cobro_venta        ON cobro(venta_id);
CREATE INDEX idx_cobro_fecha        ON cobro(fecha);
CREATE INDEX idx_cheque_estado      ON cheque(estado);
CREATE INDEX idx_cheque_fecha_cobro ON cheque(fecha_cobro);

-- ------------------------------------------------------------
--  VISTAS útiles
-- ------------------------------------------------------------

-- Stock disponible
CREATE VIEW v_stock_disponible AS
SELECT id, marca, modelo, version, anio, color, kilometraje,
       tipo, precio_venta, fecha_ingreso
FROM vehiculo
WHERE estado = 'disponible'
ORDER BY fecha_ingreso DESC;

-- Cheques pendientes con días restantes
CREATE VIEW v_cheques_pendientes AS
SELECT c.id, c.numero, c.banco, c.titular, c.monto,
       c.fecha_cobro,
       (c.fecha_cobro - CURRENT_DATE) AS dias_restantes,
       cl.nombre || ' ' || cl.apellido AS cliente
FROM cheque c
JOIN cobro co ON co.id = c.cobro_id
JOIN cliente cl ON cl.id = co.cliente_id
WHERE c.estado = 'pendiente'
ORDER BY c.fecha_cobro;

-- Resumen de cobros por mes
CREATE VIEW v_cobros_por_mes AS
SELECT DATE_TRUNC('month', fecha) AS mes,
       SUM(monto)                  AS total,
       COUNT(*)                    AS cantidad
FROM cobro
GROUP BY 1
ORDER BY 1 DESC;

-- Detalle completo de ventas
CREATE VIEW v_ventas_detalle AS
SELECT v.id, v.fecha_venta,
       cl.nombre || ' ' || cl.apellido AS cliente,
       cl.dni,
       ve.marca || ' ' || ve.modelo || ' ' || ve.anio AS vehiculo,
       ve.patente,
       v.precio_final, v.forma_pago,
       COALESCE(SUM(co.monto), 0) AS total_cobrado,
       v.precio_final - COALESCE(SUM(co.monto), 0) AS saldo_pendiente
FROM venta v
JOIN cliente cl ON cl.id = v.cliente_id
JOIN vehiculo ve ON ve.id = v.vehiculo_id
LEFT JOIN cobro co ON co.venta_id = v.id
GROUP BY v.id, cl.nombre, cl.apellido, cl.dni,
         ve.marca, ve.modelo, ve.anio, ve.patente;

