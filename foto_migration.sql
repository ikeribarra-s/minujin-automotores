-- Agrega columna de foto al stock de vehículos
ALTER TABLE vehiculo ADD COLUMN IF NOT EXISTS foto_url TEXT;
