from datetime import datetime
from typing import Optional
from sqlalchemy.sql.sqltypes import String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from pydantic import BaseModel


class Base:
    __allow_unmapped__ = True


Base = declarative_base(cls=Base)


# Definición de los modelos
class Reserva(Base):
    __tablename__ = "reserva_vuelos"

    id = Column(Integer, primary_key=True, index=True)
    passenger_name = Column(String(length=100))
    origin = Column(String(length=100))
    destination = Column(Integer)
    flight_date = Column(DateTime)
    reservation_status = Column(String(length=20))


class ReservaVuelo(BaseModel):
    __tablename__ = "reserva_vuelos"

    passenger_name: str
    origin: str
    destination: str
    flight_date: datetime
    reservation_status: Optional[str] = None


class ReservaVueloParcial(BaseModel):
    passenger_name: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    flight_date: Optional[datetime] = None
    reservation_status: Optional[str] = None


class ReservaVueloRsp(BaseModel):
    __tablename__ = "reserva_vuelos"

    id: int
    passenger_name: str
    origin: str
    destination: str
    flight_date: datetime
    reservation_status: Optional[str] = None
