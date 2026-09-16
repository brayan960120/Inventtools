from flask import url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
from src.models import session, Base
from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from src.models.detalle_facturas import DetalleFacturas
from src.models.productos import Productos
from src.models import session as db_session
from sqlalchemy.orm import relationship




class Movimientos(Base):
    __tablename__ = 'movimientos'

    id = Column(Integer, primary_key=True)
    usuario_id = Column(
        Integer,
        ForeignKey('usuarios.id'),
        nullable=False
    )
    producto_id = Column(
        Integer,
        ForeignKey('productos.id'),
        nullable=False
    )
    cantida_stock = Column(Integer, nullable=False)
    valor_unitario = Column(Float, nullable=False)
    tipo_de_movimiento = Column(String(20), nullable=False)
    fecha = Column(DateTime, default=datetime.now)
    activo = Column(Boolean, default=True)
    usuario = relationship(
        'Usuarios',
        back_populates='movimientos'
    )


    


def obtener_movimientos():

    from src.models.usuarios import Usuarios

    movimientos = (
        db_session.query(Movimientos)
        .join(
            Usuarios,
            Movimientos.usuario_id == Usuarios.id
        )
        .order_by(
            Movimientos.fecha.asc()
        )
        .all()
    )

    return movimientos


def agregar_movimiento(movimiento):
    db_session.add(movimiento)
    db_session.commit()
    return redirect(url_for('movimientos'))
 

def obtener_tipo(es_compra):
    return "Entrada" if es_compra else "Salida"


  
    
  
    
