-- ============================================================
--  Tabla de usuarios para autenticación
-- ============================================================

CREATE TABLE usuario (
    id             SERIAL PRIMARY KEY,
    username       VARCHAR(60)  UNIQUE NOT NULL,
    password_hash  VARCHAR(255) NOT NULL,
    created_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Usuario admin por defecto  (contraseña: permiso2)
INSERT INTO usuario (username, password_hash)
VALUES ('admin', '$2b$12$dJqF7BP5jM4Ak/Q6JXa3yOxD.iNz.WaA.Ql5Sx/1Gs91rN3c4AS6S');
