from datetime import datetime

from flask_login import current_user
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String
)

from sqlalchemy.orm import relationship

from src.models import Base, session


class Movimientos(Base):

    __tablename__ = "movimientos"

    id = Column(
        Integer,
        primary_key=True
    )

    usuario_id = Column(
        Integer,
        ForeignKey("usuarios.id"),
        nullable=False
    )

    producto_id = Column(
        Integer,
        ForeignKey("productos.id"),
        nullable=False
    )

    cantida_stock = Column(
        Integer,
        nullable=False
    )

    valor_unitario = Column(
        Float,
        nullable=False
    )

    tipo_de_movimiento = Column(
        String(20),
        nullable=False
    )

    fecha = Column(
        DateTime,
        default=datetime.now
    )

    activo = Column(
        Boolean,
        default=True
    )

    usuario = relationship(
        "Usuarios",
        back_populates="movimientos"
    )

def registrar_movimiento_actualizacion(producto):
    movimiento = Movimientos(
        usuario_id=current_user.id,
        producto_id=producto.id,
        cantida_stock=producto.cantida_stock,
        valor_unitario=producto.valor_unitario,
        tipo_de_movimiento="Actualización",
        fecha=datetime.datetime.now(),
        activo=True
    )

    session.add(movimiento)