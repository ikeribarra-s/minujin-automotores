export interface Vehiculo {
  id: number;
  marca: string;
  modelo: string;
  año: number;
  version: string;
  color: string;
  kilometraje: number;
  tipo: 'usado' | 'cero_km';
  procedencia: 'compra' | 'permuta' | 'consignacion';
  patente: string;
  precio_compra: number;
  precio_venta: number;
  estado: 'disponible' | 'reservado' | 'vendido';
  foto_url?: string;
  observaciones: string;
}

export interface Cliente {
  id: number;
  nombre: string;
  apellido: string;
  dni: string;
  telefono: string;
  email: string;
  direccion: string;
}

export interface Venta {
  id: number;
  vehiculo_id: number;
  cliente_id: number;
  precio_final: number;
  forma_pago: 'contado' | 'financiado' | 'permuta' | 'mixto';
  fecha_venta: string;
  observaciones: string;
}

export interface Cobro {
  id: number;
  venta_id: number;
  cliente_id: number;
  monto: number;
  fecha: string;
  concepto: 'saldo' | 'sena' | 'cuota' | 'otro';
  forma_pago: 'efectivo' | 'transferencia' | 'cheque' | 'tarjeta';
  observaciones: string;
}

export interface Cheque {
  id: number;
  numero: string;
  banco: string;
  titular: string;
  entrega: string;
  monto: number;
  fecha_emision: string;
  fecha_cobro: string;
  estado: 'pendiente' | 'cobrado' | 'depositado' | 'rechazado';
  es_cpd: boolean;
  discrepancia_monto: boolean;
  monto_letras: string;
  pagador_cuit?: string;
  beneficiario?: string;
  sucursal?: string;
  localidad?: string;
  observaciones: string;
  raw_ocr_text?: string;
  image_filename?: string;
  cobro_id?: number;
}

export let vehiculos: Vehiculo[] = [
  {
    id: 1,
    marca: 'Toyota',
    modelo: 'Corolla',
    año: 2022,
    version: 'XEi',
    color: 'Blanco',
    kilometraje: 15000,
    tipo: 'usado',
    procedencia: 'compra',
    patente: 'AB123CD',
    precio_compra: 18000000,
    precio_venta: 22000000,
    estado: 'disponible',
    observaciones: 'Excelente estado, service al día',
  },
  {
    id: 2,
    marca: 'Ford',
    modelo: 'Ranger',
    año: 2023,
    version: 'XLT 4x4',
    color: 'Negro',
    kilometraje: 8000,
    tipo: 'usado',
    procedencia: 'compra',
    patente: 'EF456GH',
    precio_compra: 35000000,
    precio_venta: 42000000,
    estado: 'reservado',
    observaciones: 'Única mano',
  },
  {
    id: 3,
    marca: 'Volkswagen',
    modelo: 'Gol Trend',
    año: 2021,
    version: 'Trendline',
    color: 'Rojo',
    kilometraje: 42000,
    tipo: 'usado',
    procedencia: 'permuta',
    patente: 'IJ789KL',
    precio_compra: 9500000,
    precio_venta: 12000000,
    estado: 'vendido',
    observaciones: '',
  },
  {
    id: 4,
    marca: 'Chevrolet',
    modelo: 'Onix',
    año: 2024,
    version: 'Premier',
    color: 'Gris',
    kilometraje: 0,
    tipo: 'cero_km',
    procedencia: 'compra',
    patente: 'MN012OP',
    precio_compra: 16000000,
    precio_venta: 19500000,
    estado: 'disponible',
    observaciones: '0km disponible para entrega inmediata',
  },
  {
    id: 5,
    marca: 'Fiat',
    modelo: 'Cronos',
    año: 2023,
    version: 'Drive',
    color: 'Azul',
    kilometraje: 25000,
    tipo: 'usado',
    procedencia: 'consignacion',
    patente: 'QR345ST',
    precio_compra: 0,
    precio_venta: 14500000,
    estado: 'disponible',
    observaciones: 'En consignación - comisión 10%',
  },
  {
    id: 6,
    marca: 'Peugeot',
    modelo: '208',
    año: 2022,
    version: 'Active',
    color: 'Blanco',
    kilometraje: 18000,
    tipo: 'usado',
    procedencia: 'compra',
    patente: 'UV678WX',
    precio_compra: 11000000,
    precio_venta: 13800000,
    estado: 'disponible',
    observaciones: '',
  },
];

export let clientes: Cliente[] = [
  {
    id: 1,
    nombre: 'Juan',
    apellido: 'Pérez',
    dni: '35123456',
    telefono: '11-5555-1234',
    email: 'juan.perez@email.com',
    direccion: 'Av. Corrientes 1234, CABA',
  },
  {
    id: 2,
    nombre: 'María',
    apellido: 'González',
    dni: '28987654',
    telefono: '11-5555-5678',
    email: 'maria.gonzalez@email.com',
    direccion: 'Calle Falsa 456, San Isidro',
  },
  {
    id: 3,
    nombre: 'Carlos',
    apellido: 'Rodríguez',
    dni: '42345678',
    telefono: '11-5555-9012',
    email: 'carlos.rodriguez@email.com',
    direccion: 'Av. Santa Fe 789, Vicente López',
  },
  {
    id: 4,
    nombre: 'Ana',
    apellido: 'Martínez',
    dni: '31234567',
    telefono: '11-5555-3456',
    email: 'ana.martinez@email.com',
    direccion: 'Belgrano 321, San Martín',
  },
];

export let ventas: Venta[] = [
  {
    id: 1,
    vehiculo_id: 3,
    cliente_id: 1,
    precio_final: 12000000,
    forma_pago: 'contado',
    fecha_venta: '2026-04-15',
    observaciones: 'Pago en efectivo',
  },
  {
    id: 2,
    vehiculo_id: 2,
    cliente_id: 2,
    precio_final: 42000000,
    forma_pago: 'financiado',
    fecha_venta: '2026-05-01',
    observaciones: 'Financiación bancaria - 36 cuotas',
  },
];

export let cobros: Cobro[] = [
  {
    id: 1,
    venta_id: 1,
    cliente_id: 1,
    monto: 3000000,
    fecha: '2026-04-15',
    concepto: 'sena',
    forma_pago: 'efectivo',
    observaciones: '',
  },
  {
    id: 2,
    venta_id: 1,
    cliente_id: 1,
    monto: 9000000,
    fecha: '2026-04-20',
    concepto: 'saldo',
    forma_pago: 'transferencia',
    observaciones: '',
  },
  {
    id: 3,
    venta_id: 2,
    cliente_id: 2,
    monto: 8000000,
    fecha: '2026-05-01',
    concepto: 'sena',
    forma_pago: 'cheque',
    observaciones: 'Cheque diferido',
  },
];

export let cheques: Cheque[] = [
  {
    id: 1,
    numero: '12345678',
    banco: 'Banco Nación',
    titular: 'María González',
    entrega: 'María González',
    monto: 8000000,
    fecha_emision: '2026-05-01',
    fecha_cobro: '2026-05-20',
    estado: 'pendiente',
    es_cpd: false,
    discrepancia_monto: false,
    monto_letras: 'Ocho millones de pesos',
    observaciones: 'Vinculado a venta #2',
    cobro_id: 3,
  },
  {
    id: 2,
    numero: '87654321',
    banco: 'Banco Galicia',
    titular: 'Carlos Rodríguez',
    entrega: 'Carlos Rodríguez',
    monto: 2500000,
    fecha_emision: '2026-04-10',
    fecha_cobro: '2026-05-25',
    estado: 'pendiente',
    es_cpd: true,
    discrepancia_monto: false,
    monto_letras: 'Dos millones quinientos mil pesos',
    observaciones: '',
  },
  {
    id: 3,
    numero: '11223344',
    banco: 'Banco Santander',
    titular: 'Ana Martínez',
    entrega: 'Ana Martínez',
    monto: 1800000,
    fecha_emision: '2026-03-15',
    fecha_cobro: '2026-05-18',
    estado: 'pendiente',
    es_cpd: false,
    discrepancia_monto: false,
    monto_letras: 'Un millón ochocientos mil pesos',
    observaciones: '',
  },
  {
    id: 4,
    numero: '55667788',
    banco: 'Banco BBVA',
    titular: 'Juan Pérez',
    entrega: 'Juan Pérez',
    monto: 3200000,
    fecha_emision: '2026-04-01',
    fecha_cobro: '2026-04-30',
    estado: 'cobrado',
    es_cpd: false,
    discrepancia_monto: false,
    monto_letras: 'Tres millones doscientos mil pesos',
    observaciones: 'Cobrado en efectivo',
  },
];
