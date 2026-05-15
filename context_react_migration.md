# Minujin Automotores — React Frontend Migration Context

You are building the React/TypeScript frontend for an internal car dealership management system called **Minujin Automotores**. The backend already exists and is fully functional. Your job is to connect the new React app to it.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend (new) | React + TypeScript + Vite (`localhost:5173`) |
| Backend (existing) | FastAPI + Python 3.11, running at `http://localhost:8000` |
| Database | PostgreSQL via Supabase |
| Auth | JWT — Bearer token, expires in 480 min |
| File storage | Supabase Storage (vehicle photos) |

---

## Authentication

### Login
```
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=xxx&password=xxx
```
Response:
```json
{ "access_token": "eyJ...", "token_type": "bearer" }
```

All other endpoints require the header:
```
Authorization: Bearer <access_token>
```

On 401 → redirect to login and clear stored token.

Store the token in `localStorage` (or a React context + localStorage). There is only one user account — no registration flow needed.

---

## API Base URL

```
http://localhost:8000
```

Set this as an env variable: `VITE_API_URL=http://localhost:8000`

CORS is fully open on the backend (`allow_origins=["*"]`), so no proxy needed during development.

---

## API Reference

All monetary values are returned as strings (Decimal serialization from Python). Parse with `parseFloat()`.  
All dates are ISO 8601 strings (`YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SS`).

---

### VEHICULOS `/vehiculos`

#### GET /vehiculos/
Optional query param: `estado=disponible|reservado|vendido`  
Returns array of VehiculoResponse (ordered by fecha_ingreso desc).

#### GET /vehiculos/{id}
Returns single VehiculoResponse.

#### POST /vehiculos/
Body (JSON):
```ts
{
  marca: string            // required
  modelo: string           // required
  anio: number             // required
  version?: string
  color?: string
  kilometraje?: number     // default 0
  tipo: "usado" | "cero_km"
  procedencia: "compra" | "permuta" | "consignacion"
  patente?: string         // validated: "AB 123 CD" or "ABC 123"
  precio_compra?: number
  precio_venta?: number
  estado?: "disponible" | "reservado" | "vendido"  // default "disponible"
  observaciones?: string
}
```

#### PUT /vehiculos/{id}
Same fields as POST, all optional (partial update).

#### DELETE /vehiculos/{id}
Returns 204. Fails with 409 if vehicle is "vendido" or "reservado".

#### POST /vehiculos/{id}/foto
`multipart/form-data`, field name: `file` (image: jpg/jpeg/png/webp).  
Uploads to Supabase Storage, sets `foto_url` on vehicle. Returns updated VehiculoResponse.

#### VehiculoResponse shape:
```ts
interface Vehiculo {
  id: number
  marca: string
  modelo: string
  version: string | null
  anio: number
  color: string | null
  kilometraje: number
  tipo: "usado" | "cero_km"
  procedencia: "compra" | "permuta" | "consignacion"
  patente: string | null        // normalized, e.g. "AB 123 CD"
  precio_compra: string | null  // parse as float
  precio_venta: string | null   // parse as float
  estado: "disponible" | "reservado" | "vendido"
  foto_url: string | null
  observaciones: string | null
  fecha_ingreso: string         // YYYY-MM-DD
  created_at: string
  updated_at: string
}
```

---

### CLIENTES `/clientes`

#### GET /clientes/
Optional query param: `busqueda=string` (searches nombre, apellido, DNI — case insensitive).  
Returns array ordered by apellido.

#### GET /clientes/{id}
#### POST /clientes/
#### PUT /clientes/{id}

```ts
interface Cliente {
  id: number
  nombre: string
  apellido: string
  dni: string | null
  telefono: string | null
  email: string | null
  direccion: string | null
}
```
POST/PUT body: same fields, `nombre` and `apellido` required.

#### DELETE /clientes/{id}
Returns 204. Fails with 409 if client has associated ventas.

---

### VENTAS `/ventas`

#### GET /ventas/
Returns all ventas ordered by fecha_venta desc.

#### GET /ventas/{id}

#### POST /ventas/
```ts
{
  vehiculo_id: number   // required — must be "disponible"
  cliente_id: number    // required
  precio_final: number  // required
  forma_pago: "contado" | "financiado" | "permuta" | "mixto"
  observaciones?: string
}
```
Note: creates the venta and automatically marks the vehiculo as "vendido".

#### PUT /ventas/{id}
Only these fields are editable:
```ts
{
  precio_final?: number
  forma_pago?: "contado" | "financiado" | "permuta" | "mixto"
  observaciones?: string
}
```

```ts
interface Venta {
  id: number
  vehiculo_id: number
  cliente_id: number
  precio_final: string   // parse as float
  forma_pago: "contado" | "financiado" | "permuta" | "mixto"
  fecha_venta: string    // YYYY-MM-DD
  observaciones: string | null
  created_at: string
}
```

---

### COBROS `/cobros`

#### GET /cobros/
Optional query param: `venta_id=number`  
Returns array ordered by fecha desc.

#### GET /cobros/{id}

#### POST /cobros/
```ts
{
  venta_id: number
  cliente_id: number
  monto: number           // required — validated: cannot exceed venta.precio_final - already_collected
  concepto: "sena" | "saldo" | "cuota" | "otro"
  forma_pago: "efectivo" | "transferencia" | "cheque" | "tarjeta"
  observaciones?: string
}
```
Backend validates: total collected across all cobros for the venta cannot exceed venta.precio_final. Returns 400 with remaining balance if exceeded.

#### PATCH /cobros/{id}
Editable fields only:
```ts
{
  monto?: number
  concepto?: "sena" | "saldo" | "cuota" | "otro"
  forma_pago?: "efectivo" | "transferencia" | "cheque" | "tarjeta"
  observaciones?: string
}
```

```ts
interface Cobro {
  id: number
  venta_id: number
  cliente_id: number
  monto: string       // parse as float
  concepto: "sena" | "saldo" | "cuota" | "otro"
  forma_pago: "efectivo" | "transferencia" | "cheque" | "tarjeta"
  fecha: string       // YYYY-MM-DD
  observaciones: string | null
  created_at: string
}
```

---

### CHEQUES `/cheques`

#### GET /cheques/
Optional query param: `estado=pendiente|cobrado|depositado|rechazado`  
Returns array ordered by fecha_cobro asc.

#### GET /cheques/{id}

#### POST /cheques/
```ts
{
  numero: string          // required
  banco: string           // required
  cobro_id?: number       // optional — cheques can exist without a cobro
  titular?: string
  entrega?: string        // who physically handed over the cheque
  monto: number           // required
  fecha_cobro: string     // required — YYYY-MM-DD
  fecha_emision?: string
  monto_letras?: string
  pagador_cuit?: string
  beneficiario?: string
  sucursal?: string
  localidad?: string
  es_cpd?: boolean
  discrepancia_monto?: boolean
  observaciones?: string
  raw_ocr_text?: string
  raw_json?: string
}
```

#### PATCH /cheques/{id}
All fields optional. Commonly used to update `estado`.

#### POST /cheques/scan
`multipart/form-data`, field name: `file` (image: jpg/jpeg/png/webp).  
AI-powered (Google Vision + Claude). Returns ScanResult — does NOT write to DB.  
The UI should show the result in a form for user review before calling POST /cheques/ to save.

```ts
interface ScanResult {
  tipo: string | null           // "cheque" | "pagare"
  banco: string | null
  numero: string | null
  monto_numerico: string | null // parse as float
  monto_letras: string | null
  fecha_emision: string | null  // YYYY-MM-DD
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
  warning: string | null        // shown to user if OCR fell back to Claude
}
```

This endpoint can take up to 30 seconds — use a long timeout (120s recommended).

```ts
interface Cheque {
  id: number
  cobro_id: number | null
  numero: string
  banco: string
  titular: string | null
  entrega: string | null
  monto: string               // parse as float
  fecha_cobro: string         // YYYY-MM-DD
  fecha_emision: string | null
  estado: "pendiente" | "cobrado" | "depositado" | "rechazado"
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
```

---

### PERMUTAS `/permutas`

#### GET /permutas/
#### GET /permutas/{id}
#### POST /permutas/
```ts
{
  venta_id: number
  vehiculo_recibido_id: number  // must exist in vehiculos table
  valor_tasacion: number
  observaciones?: string
}
```

```ts
interface Permuta {
  id: number
  venta_id: number
  vehiculo_recibido_id: number
  valor_tasacion: string    // parse as float
  observaciones: string | null
  created_at: string
}
```

---

## Pages & Routing

```
/login                  → Login page (unauthenticated)
/                       → redirect to /dashboard
/dashboard              → KPIs + charts + upcoming cheques
/stock                  → Vehicle inventory
/clientes               → Client list
/ventas                 → Sales list
/cobros                 → Payments list
/cheques                → Cheque portfolio
```

Private routes: redirect to `/login` if no token.

---

## Dashboard Page — Data Requirements

This is the most complex page. It needs data from multiple endpoints loaded in parallel:

```ts
const [ventas, cobros, vehiculos, chequesPendientes] = await Promise.all([
  api.get('/ventas/'),
  api.get('/cobros/'),
  api.get('/vehiculos/'),
  api.get('/cheques/', { params: { estado: 'pendiente' } }),
])
```

### KPI Cards (4 metrics)
1. **Cobrado este mes** — sum of `cobros.monto` where `cobros.fecha` starts with current `YYYY-MM`. Delta vs previous month.
2. **Ventas del mes** — count of `ventas` where `fecha_venta` starts with current `YYYY-MM`.
3. **Margen bruto del mes** — for each venta this month, find the matching vehiculo by `vehiculo_id` and compute `precio_final - precio_compra`. Sum all.
4. **Cheques a cobrar (30d)** — sum of `chequesPendientes.monto` where `fecha_cobro` is between today and today+30 days.

### Charts
- **Cobros por mes (6 months)**: stacked bar, x=month, y=monto, color=forma_pago
- **Facturación por mes (6 months)**: bar chart, x=month, y=precio_final, label=count of ventas
- **Cobros por forma de pago**: donut chart, segments per forma_pago
- **Stock por estado**: donut chart, disponible/reservado/vendido
- **Margen por venta (last 10)**: bar chart, green=positive margin, red=negative

### Upcoming Cheques section
Show up to 4 cheques from `chequesPendientes` with `fecha_cobro` within 30 days, sorted by date.
Each row has an inline estado selector + save button (PATCH /cheques/{id}).

**Important**: The dashboard error `Cannot read properties of undefined (reading 'ventas')` means a Recharts label formatter is receiving `undefined` instead of a data object. Always guard formatters:
```ts
// WRONG:
formatter={(value, name, props) => props.payload.ventas}

// CORRECT:
formatter={(value, name, props) => props?.payload?.ventas ?? value}
```

---

## UI Design System

**Target**: Clean, white, modern — similar to Linear/Vercel dashboards.

| Token | Value |
|---|---|
| Accent / CTA | `#FF6B2B` (brand orange) |
| Success / Disponible | `#22C55E` |
| Warning / Pendiente / Reservado | `#F59E0B` |
| Danger / Rechazado | `#EF4444` |
| Info / Depositado / Financiado | `#3B82F6` |
| Gray text | `#6B7280` |
| Font | Inter or DM Sans |
| Border radius | 8–12px |
| Cards | white bg, light border, soft shadow |

**Status badges**: pill shape, uppercase, small font, color-coded tinted background.

**Edit flow**: list row → click Edit → modal opens pre-filled → Save → close modal → refresh list → success toast.

**Mobile**: nav bar scrolls horizontally only. Inputs min font-size 16px (prevents iOS zoom).

---

## Common Patterns

### API client (suggested)
```ts
// api.ts
const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

function getToken() {
  return localStorage.getItem('token')
}

async function request(method: string, path: string, options: RequestInit = {}, params?: Record<string, string>) {
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
    throw new Error('Unauthorized')
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
  post: (path: string, body: unknown) => request('POST', path, { body: JSON.stringify(body) }),
  put: (path: string, body: unknown) => request('PUT', path, { body: JSON.stringify(body) }),
  patch: (path: string, body: unknown) => request('PATCH', path, { body: JSON.stringify(body) }),
  delete: (path: string) => request('DELETE', path),
}

export async function uploadFile(path: string, file: File, timeout = 120_000): Promise<unknown> {
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
  if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail ?? `HTTP ${res.status}`)
  return res.json()
}
```

### Login
```ts
// POST with x-www-form-urlencoded (NOT JSON — this is OAuth2 standard)
const form = new URLSearchParams({ username, password })
const res = await fetch(`${BASE}/auth/token`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: form,
})
const data = await res.json()
localStorage.setItem('token', data.access_token)
```

### Formatting
```ts
// Argentine peso
const fmt = (v: number) => '$ ' + v.toLocaleString('es-AR', { maximumFractionDigits: 0 })

// Parse API decimal strings
const parseDecimal = (v: string | null) => v ? parseFloat(v) : 0
```

---

## Known Issues to Fix

1. **Dashboard Recharts crash** (`Cannot read properties of undefined (reading 'ventas')`):  
   A label formatter in `Dashboard.tsx:284` accesses `props.payload.ventas` without null guard.  
   Fix: `props?.payload?.ventas ?? value` — or better, check that your data array is fully populated before rendering the chart. Load state should be `idle → loading → success/error`, charts only render on `success`.

2. **Cheque scan timeout**: The `/cheques/scan` endpoint can take 20–30 seconds (Claude API). Set `AbortController` timeout to 120 seconds, and show a spinner with a message like "Procesando con IA…".

---

## Running the Backend Locally

```bash
# From project root: minujin-automotores/
.venv/Scripts/uvicorn backend.main:app --reload --port 8000

# Or with the run script (check run.txt in repo root)
```

The backend needs a `.env` file with:
```
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=...
ANTHROPIC_API_KEY=...         # for cheque scanner
SUPABASE_URL=...              # for vehicle photo storage
SUPABASE_KEY=...
```

---

## Project File Structure (backend)

```
minujin-automotores/
├── backend/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── auth.py              # JWT create/verify
│   ├── config.py            # Settings from .env
│   ├── database.py          # SQLAlchemy async engine + session
│   ├── models/
│   │   ├── enums.py         # All enum definitions
│   │   ├── vehiculo.py
│   │   ├── cliente.py
│   │   ├── venta.py
│   │   ├── cobro.py
│   │   ├── cheque.py
│   │   ├── permuta.py
│   │   └── usuario.py
│   ├── schemas/             # Pydantic request/response models
│   ├── routers/             # One file per entity
│   └── scanner/             # OCR + Claude extraction for cheques
├── frontend/                # OLD Streamlit frontend (being replaced)
└── .venv/                   # Python virtual environment
```
