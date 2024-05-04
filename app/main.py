from fastapi import FastAPI, HTTPException, Depends
from typing import List
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
from .models import (
    Base,
    Reserva,
    ReservaVuelo,
    ReservaVueloParcial,
    ReservaVueloRsp
    )
import tempfile


# Crea un archivo temporal para la base de datos
temp_db_file = tempfile.mktemp()


# Configuración de la base de datos
SQLALCHEMY_DATABASE_URL = f"sqlite:///{temp_db_file}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Crea la tabla si no existe
Base.metadata.create_all(bind=engine)


# Función para obtener una sesión de la base de datos
def get_db():
    db = SessionLocal()
    return db


# Inicializa la aplicación FastAPI
app = FastAPI(root_path="/api")


def last_id_inserted():

    session = SessionLocal()

    try:
        ultimo_registro = session.query(Reserva).order_by(
            Reserva.id.desc()).first()
        if ultimo_registro:
            return ultimo_registro.id
        else:
            return None
    finally:
        session.close()


@app.get("/")
async def read_root():
    return "Bienvenido a la página de reservas"


# Rutas para operaciones CRUD
@app.get("/reservas/", response_model=List[ReservaVueloRsp])
def listar_reservas(skip: int = 0, limit: int = 10,
                    db: Session = Depends(get_db)):
    reservas = db.query(Reserva).offset(skip).limit(limit).all()
    return reservas


@app.post("/reservas/", response_model=ReservaVueloRsp)
def crear_reserva(reserva: ReservaVuelo, db: Session = Depends(get_db)):
    db_reserva = Reserva(**reserva.dict())
    db.add(db_reserva)
    db.commit()
    db.refresh(db_reserva)
    reserva_id = last_id_inserted()
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    return db_reserva


@app.get("/reservas/{reserva_id}", response_model=ReservaVueloRsp)
async def obtener_reserva(reserva_id: int, db: Session = Depends(get_db)):
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return db_reserva


@app.put("/reservas/{reserva_id}", response_model=ReservaVueloRsp)
async def actualizar_reserva(reserva_id: int, reserva: ReservaVuelo,
                             db: Session = Depends(get_db)):
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db_reserva.passenger_name = reserva.passenger_name
    db_reserva.origin = reserva.origin
    db_reserva.destination = reserva.destination
    db_reserva.flight_date = reserva.flight_date
    db_reserva.reservation_status = reserva.reservation_status
    db.commit()
    return db_reserva


@app.patch("/reservas/{reserva_id}", response_model=ReservaVueloRsp)
async def actualizar_reserva_parcial(reserva_id: int,
                                     reserva_parcial: ReservaVueloParcial,
                                     db: Session = Depends(get_db)):
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    # Actualiza solo los campos proporcionados en la solicitud
    for field, value in reserva_parcial.dict().items():
        if value is not None:
            setattr(db_reserva, field, value)

    db.commit()
    db.refresh(db_reserva)
    return db_reserva


@app.delete("/reservas/{reserva_id}")
async def eliminar_reserva(reserva_id: int, db: Session = Depends(get_db)):
    db_reserva = db.query(Reserva).filter(Reserva.id == reserva_id).first()
    if db_reserva is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    db.delete(db_reserva)
    db.commit()
    return {"message": "Reserva eliminada"}
