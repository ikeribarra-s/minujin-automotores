"""
Seed script — crea datos de prueba via la API REST.
Uso:
    python seed_data.py
    python seed_data.py --url http://localhost:8000 --user admin --password secret
"""
import argparse
import sys
import json
from datetime import date, timedelta
import urllib.request
import urllib.parse
import urllib.error

# ── helpers ──────────────────────────────────────────────────────────────────

def req(method, url, body=None, token=None):
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as res:
            return json.loads(res.read())
    except urllib.error.HTTPError as e:
        msg = e.read().decode()
        try:
            detail = json.loads(msg).get("detail", msg)
        except Exception:
            detail = msg
        print(f"  ERROR {method} {url} -> {e.code}: {detail}")
        return None

def get(url, token=None, params=None):
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return req("GET", url, token=token)

def post(url, body, token):
    return req("POST", url, body=body, token=token)

def ok(label, obj):
    if obj:
        print(f"  OK {label} #{obj['id']}")
    return obj

def days_from_now(n):
    return (date.today() + timedelta(days=n)).isoformat()

# ── seed data ─────────────────────────────────────────────────────────────────

def run(base, username, password):
    # 1. Login
    print("\n-- Login -------------------------------------")
    form = urllib.parse.urlencode({"username": username, "password": password}).encode()
    r = urllib.request.Request(
        f"{base}/auth/token",
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(r) as res:
            token = json.loads(res.read())["access_token"]
            print(f"  OK Token obtenido")
    except urllib.error.HTTPError as e:
        print(f"  ERROR Login fallo ({e.code}): {e.read().decode()}")
        sys.exit(1)

    # 2. Clientes
    print("\n-- Clientes ----------------------------------")
    clientes_data = [
        {"nombre": "Juan",    "apellido": "Pérez",      "dni": "35123456", "telefono": "11-5555-1234", "email": "juan.perez@gmail.com",      "direccion": "Av. Corrientes 1234, CABA"},
        {"nombre": "María",   "apellido": "González",   "dni": "28987654", "telefono": "11-5555-5678", "email": "maria.gonzalez@gmail.com",   "direccion": "Calle Falsa 456, San Isidro"},
        {"nombre": "Carlos",  "apellido": "Rodríguez",  "dni": "42345678", "telefono": "11-5555-9012", "email": "carlos.rodriguez@gmail.com", "direccion": "Av. Santa Fe 789, Vicente López"},
        {"nombre": "Ana",     "apellido": "Martínez",   "dni": "31234567", "telefono": "11-5555-3456", "email": "ana.martinez@gmail.com",     "direccion": "Belgrano 321, San Martín"},
        {"nombre": "Roberto", "apellido": "Sánchez",    "dni": "39876543", "telefono": "11-5555-7890", "email": "roberto.sanchez@gmail.com",  "direccion": "Mitre 567, Quilmes"},
    ]
    clientes = []
    for c in clientes_data:
        obj = ok(f"{c['apellido']}, {c['nombre']}", post(f"{base}/clientes/", c, token))
        if obj:
            clientes.append(obj)

    if len(clientes) < 3:
        print("❌ No se pudieron crear suficientes clientes. Abortando.")
        sys.exit(1)

    # 3. Vehiculos
    print("\n-- Vehiculos ---------------------------------")
    vehiculos_data = [
        # disponibles
        {"marca": "Toyota",    "modelo": "Corolla",    "anio": 2022, "version": "XEi",       "color": "Blanco",   "kilometraje": 15000, "tipo": "usado",    "procedencia": "compra",       "patente": "AB 123 CD", "precio_compra": 18000000, "precio_venta": 22000000, "observaciones": "Service al día, único dueño"},
        {"marca": "Chevrolet", "modelo": "Onix",       "anio": 2024, "version": "Premier",   "color": "Gris",     "kilometraje": 0,     "tipo": "cero_km",  "procedencia": "compra",       "patente": "MN 012 OP", "precio_compra": 16000000, "precio_venta": 19500000, "observaciones": "0km entrega inmediata"},
        {"marca": "Fiat",      "modelo": "Cronos",     "anio": 2023, "version": "Drive",     "color": "Azul",     "kilometraje": 25000, "tipo": "usado",    "procedencia": "consignacion", "patente": "QR 345 ST", "precio_compra": None,     "precio_venta": 16000000, "observaciones": "En consignación — comisión 10%"},
        {"marca": "Peugeot",   "modelo": "208",        "anio": 2022, "version": "Active",    "color": "Blanco",   "kilometraje": 18000, "tipo": "usado",    "procedencia": "compra",       "patente": "UV 678 WX", "precio_compra": 11000000, "precio_venta": 13800000, "observaciones": ""},
        {"marca": "Renault",   "modelo": "Sandero",    "anio": 2023, "version": "Intens",    "color": "Rojo",     "kilometraje": 8000,  "tipo": "usado",    "procedencia": "compra",       "patente": "YZ 901 AB", "precio_compra": 10000000, "precio_venta": 12500000, "observaciones": ""},
        # estos tres se van a vender
        {"marca": "Ford",      "modelo": "Ranger",     "anio": 2023, "version": "XLT 4x4",  "color": "Negro",    "kilometraje": 8000,  "tipo": "usado",    "procedencia": "compra",       "patente": "EF 456 GH", "precio_compra": 35000000, "precio_venta": 42000000, "observaciones": "Única mano"},
        {"marca": "Volkswagen","modelo": "Gol Trend",  "anio": 2021, "version": "Trendline", "color": "Rojo",     "kilometraje": 42000, "tipo": "usado",    "procedencia": "permuta",      "patente": "IJ 789 KL", "precio_compra": 9500000,  "precio_venta": 12000000, "observaciones": ""},
        {"marca": "Honda",     "modelo": "Civic",      "anio": 2020, "version": "EX",        "color": "Plateado", "kilometraje": 55000, "tipo": "usado",    "procedencia": "compra",       "patente": "CD 234 EF", "precio_compra": 14000000, "precio_venta": 17500000, "observaciones": "Permiso de transferencia listo"},
    ]
    vehiculos = []
    for v in vehiculos_data:
        obj = ok(f"{v['marca']} {v['modelo']} {v['anio']}", post(f"{base}/vehiculos/", v, token))
        if obj:
            vehiculos.append(obj)

    if len(vehiculos) < 6:
        print("❌ No se pudieron crear suficientes vehículos. Abortando.")
        sys.exit(1)

    # índices: 5=Ranger, 6=Gol, 7=Civic (los que se venden)
    v_ranger = vehiculos[5]
    v_gol    = vehiculos[6]
    v_civic  = vehiculos[7]

    c_juan   = clientes[0]
    c_maria  = clientes[1]
    c_carlos = clientes[2]
    c_ana    = clientes[3]

    # 4. Ventas
    print("\n-- Ventas ------------------------------------")
    ventas_data = [
        {"vehiculo_id": v_ranger["id"], "cliente_id": c_carlos["id"], "precio_final": 40000000, "forma_pago": "mixto",      "observaciones": "Parte en cheques, parte transferencia"},
        {"vehiculo_id": v_gol["id"],    "cliente_id": c_juan["id"],   "precio_final": 12000000, "forma_pago": "contado",    "observaciones": "Pago completo en efectivo"},
        {"vehiculo_id": v_civic["id"],  "cliente_id": c_maria["id"],  "precio_final": 17500000, "forma_pago": "financiado", "observaciones": "Financiación bancaria — 24 cuotas"},
    ]
    ventas = []
    for v in ventas_data:
        obj = post(f"{base}/ventas/", v, token)
        if obj:
            print(f"  ✓ Venta #{obj['id']} — {v['forma_pago']} ${v['precio_final']:,}")
            ventas.append(obj)

    if not ventas:
        print("❌ No se crearon ventas.")
        sys.exit(1)

    venta_ranger = ventas[0]  # 40M mixto
    venta_gol    = ventas[1]  # 12M contado
    venta_civic  = ventas[2]  # 17.5M financiado

    # 5. Cobros
    print("\n-- Cobros ------------------------------------")
    cobros_data = [
        # Ranger 40M: seña 8M + cuota 12M transferencia + cuota 10M cheque
        {"venta_id": venta_ranger["id"], "cliente_id": c_carlos["id"], "monto": 8000000,  "concepto": "sena",  "forma_pago": "efectivo",      "observaciones": "Seña entrega del vehículo"},
        {"venta_id": venta_ranger["id"], "cliente_id": c_carlos["id"], "monto": 12000000, "concepto": "cuota", "forma_pago": "transferencia",  "observaciones": "Transferencia Banco Nación"},
        {"venta_id": venta_ranger["id"], "cliente_id": c_carlos["id"], "monto": 10000000, "concepto": "cuota", "forma_pago": "cheque",         "observaciones": "Cheque diferido 30 días"},
        # Gol 12M: saldo completo
        {"venta_id": venta_gol["id"],    "cliente_id": c_juan["id"],   "monto": 12000000, "concepto": "saldo", "forma_pago": "efectivo",       "observaciones": ""},
        # Civic 17.5M: seña 3.5M + cuota 7M cheque
        {"venta_id": venta_civic["id"],  "cliente_id": c_maria["id"],  "monto": 3500000,  "concepto": "sena",  "forma_pago": "efectivo",       "observaciones": ""},
        {"venta_id": venta_civic["id"],  "cliente_id": c_maria["id"],  "monto": 7000000,  "concepto": "cuota", "forma_pago": "cheque",         "observaciones": "Cheque posdatado"},
    ]
    cobros = []
    for c in cobros_data:
        obj = post(f"{base}/cobros/", c, token)
        if obj:
            print(f"  ✓ Cobro #{obj['id']} — {c['concepto']} ${c['monto']:,} ({c['forma_pago']})")
            cobros.append(obj)

    cobro_ranger_cheque = cobros[2] if len(cobros) > 2 else None  # 10M cheque
    cobro_civic_cheque  = cobros[5] if len(cobros) > 5 else None  # 7M cheque

    # 6. Cheques
    print("\n-- Cheques -----------------------------------")
    cheques_data = [
        # vinculado al cobro del Ranger
        {
            "cobro_id":    cobro_ranger_cheque["id"] if cobro_ranger_cheque else None,
            "numero":      "00012345678",
            "banco":       "Banco Nación",
            "titular":     "Carlos Rodríguez",
            "entrega":     "Carlos Rodríguez",
            "monto":       10000000,
            "fecha_cobro": days_from_now(25),
            "fecha_emision": days_from_now(-5),
            "monto_letras": "Diez millones de pesos",
            "es_cpd":       False,
            "observaciones": "Vinculado a Venta Ranger",
        },
        # vinculado al cobro del Civic
        {
            "cobro_id":    cobro_civic_cheque["id"] if cobro_civic_cheque else None,
            "numero":      "00087654321",
            "banco":       "Banco Galicia",
            "titular":     "María González",
            "entrega":     "María González",
            "monto":       7000000,
            "fecha_cobro": days_from_now(12),
            "fecha_emision": days_from_now(-3),
            "monto_letras": "Siete millones de pesos",
            "es_cpd":       True,
            "observaciones": "CPD — Civic financiado",
        },
        # cheque standalone próximo a vencer (urgente)
        {
            "numero":      "00011223344",
            "banco":       "Banco Santander",
            "titular":     "Ana Martínez",
            "entrega":     "Ana Martínez",
            "monto":       3500000,
            "fecha_cobro": days_from_now(3),
            "fecha_emision": days_from_now(-10),
            "monto_letras": "Tres millones quinientos mil pesos",
            "es_cpd":       False,
            "observaciones": "",
        },
        # cheque ya cobrado (histórico)
        {
            "numero":      "00055667788",
            "banco":       "Banco BBVA",
            "titular":     "Juan Pérez",
            "entrega":     "Juan Pérez",
            "monto":       2000000,
            "fecha_cobro": days_from_now(-15),
            "monto_letras": "Dos millones de pesos",
            "es_cpd":       False,
            "observaciones": "Ya acreditado",
        },
        # cheque pendiente a 45 días
        {
            "numero":      "00099887766",
            "banco":       "Banco Macro",
            "titular":     "Roberto Sánchez",
            "entrega":     "Roberto Sánchez",
            "monto":       5000000,
            "fecha_cobro": days_from_now(45),
            "fecha_emision": days_from_now(-1),
            "monto_letras": "Cinco millones de pesos",
            "es_cpd":       True,
            "observaciones": "Cheque posdatado 45 días",
        },
    ]
    cheques = []
    for ch in cheques_data:
        obj = post(f"{base}/cheques/", ch, token)
        if obj:
            print(f"  OK Cheque #{obj['id']} - {ch['banco']} N {ch['numero']} ${ch['monto']:,} vence {ch['fecha_cobro']}")
            cheques.append(obj)

    # Marcar el cheque histórico como cobrado
    if len(cheques) >= 4:
        ch_cobrado = cheques[3]
        import urllib.request as ur
        data = json.dumps({"estado": "cobrado"}).encode()
        patch_req = ur.Request(
            f"{base}/cheques/{ch_cobrado['id']}",
            data=data,
            headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
            method="PATCH",
        )
        try:
            with ur.urlopen(patch_req) as res:
                print(f"  OK Cheque #{ch_cobrado['id']} marcado como cobrado")
        except Exception as e:
            print(f"  WARN No se pudo marcar cheque como cobrado: {e}")

    # Resumen
    print("\n" + "=" * 45)
    print("  SEED COMPLETADO")
    print("=" * 45)
    print(f"  Clientes  : {len(clientes)}")
    print(f"  Vehiculos : {len(vehiculos)}  ({len(vehiculos)-3} disponibles + 3 vendidos)")
    print(f"  Ventas    : {len(ventas)}")
    print(f"  Cobros    : {len(cobros)}")
    print(f"  Cheques   : {len(cheques)}  (3 proximos 30d + 1 cobrado + 1 a 45d)")
    print("=" * 45)
    print(f"\n  Frontend → http://localhost:5173")
    print(f"  Backend  → {base}/docs\n")


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed de datos de prueba")
    parser.add_argument("--url",      default="http://localhost:8000", help="URL base del backend")
    parser.add_argument("--user",     default="",  help="Usuario")
    parser.add_argument("--password", default="",  help="Contraseña")
    args = parser.parse_args()

    url  = args.url.rstrip("/")
    user = args.user     or input("Usuario: ")
    pwd  = args.password or input("Contraseña: ")

    print(f"\nConectando a {url} ...")
    run(url, user, pwd)
