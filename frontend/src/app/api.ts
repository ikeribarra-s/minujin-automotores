const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('token')
}

async function request(
  method: string,
  path: string,
  options: RequestInit = {},
  params?: Record<string, string>
) {
  const url = new URL(BASE + path)
  if (params) Object.entries(params).forEach(([k, v]) => url.searchParams.set(k, v))

  const res = await fetch(url.toString(), {
    method,
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getToken()}`,
      ...options.headers,
    },
    ...options,
  })

  if (res.status === 401) {
    localStorage.removeItem('token')
    window.location.href = '/login'
    throw new Error('Sesión expirada')
  }
  if (res.status === 204) return null
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export const api = {
  get: (path: string, params?: Record<string, string>) => request('GET', path, {}, params),
  post: (path: string, body: unknown) =>
    request('POST', path, { body: JSON.stringify(body) }),
  put: (path: string, body: unknown) =>
    request('PUT', path, { body: JSON.stringify(body) }),
  patch: (path: string, body: unknown) =>
    request('PATCH', path, { body: JSON.stringify(body) }),
  delete: (path: string) => request('DELETE', path),
}

export async function uploadFile(
  path: string,
  file: File,
  timeout = 120_000
): Promise<unknown> {
  const form = new FormData()
  form.append('file', file)
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeout)
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { Authorization: `Bearer ${getToken()}` },
    body: form,
    signal: controller.signal,
  })
  clearTimeout(timer)
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail ?? `HTTP ${res.status}`)
  }
  return res.json()
}

export const parseDecimal = (v: string | null | undefined): number =>
  v ? parseFloat(v) : 0

// ── Types matching API responses ──────────────────────────────────────────────

export interface Vehiculo {
  id: number
  marca: string
  modelo: string
  version: string | null
  anio: number
  color: string | null
  kilometraje: number
  tipo: 'usado' | 'cero_km'
  procedencia: 'compra' | 'permuta' | 'consignacion'
  patente: string | null
  precio_compra: string | null
  precio_venta: string | null
  estado: 'disponible' | 'reservado' | 'vendido'
  foto_url: string | null
  observaciones: string | null
  fecha_ingreso: string
  created_at: string
  updated_at: string
}

export interface Cliente {
  id: number
  nombre: string
  apellido: string
  dni: string | null
  telefono: string | null
  email: string | null
  direccion: string | null
}

export interface Venta {
  id: number
  vehiculo_id: number
  cliente_id: number
  precio_final: string
  forma_pago: 'contado' | 'financiado' | 'permuta' | 'mixto'
  fecha_venta: string
  observaciones: string | null
  created_at: string
}

export interface Cobro {
  id: number
  venta_id: number
  cliente_id: number
  monto: string
  concepto: 'sena' | 'saldo' | 'cuota' | 'otro'
  forma_pago: 'efectivo' | 'transferencia' | 'cheque' | 'tarjeta'
  fecha: string
  observaciones: string | null
  created_at: string
}

export interface Cheque {
  id: number
  cobro_id: number | null
  numero: string
  banco: string
  titular: string | null
  entrega: string | null
  monto: string
  fecha_cobro: string
  fecha_emision: string | null
  estado: 'pendiente' | 'cobrado' | 'depositado' | 'rechazado'
  monto_letras: string | null
  pagador_cuit: string | null
  beneficiario: string | null
  sucursal: string | null
  localidad: string | null
  es_cpd: boolean
  discrepancia_monto: boolean
  observaciones: string | null
  raw_ocr_text: string | null
  image_filename: string | null
  created_at: string
  updated_at: string
}

export interface Pagare {
  id: number
  numero: string
  monto: string
  vencimiento: string
  firmante: string | null
  calle: string | null
  localidad: string | null
  estado: 'pendiente' | 'cobrado' | 'rechazado'
  observaciones: string | null
  raw_ocr_text: string | null
  image_filename: string | null
  created_at: string
  updated_at: string
}

export interface ScanResult {
  tipo: string | null
  banco: string | null
  numero: string | null
  monto_numerico: string | null
  monto_letras: string | null
  fecha_emision: string | null
  fecha_vencimiento: string | null
  pagador_nombre: string | null
  pagador_cuit: string | null
  beneficiario: string | null
  sucursal: string | null
  localidad: string | null
  es_cpd: boolean
  discrepancia_monto: boolean
  raw_ocr_text: string
  raw_json: object | null
  warning: string | null
}
