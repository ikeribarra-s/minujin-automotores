from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import auth, vehiculo, cliente, venta, cobro, cheque, permuta, pagare

app = FastAPI(title="Automotora API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vehiculo.router)
app.include_router(cliente.router)
app.include_router(venta.router)
app.include_router(cobro.router)
app.include_router(cheque.router)
app.include_router(permuta.router)
app.include_router(pagare.router)


@app.get("/")
async def root():
    return {"status": "ok"}
