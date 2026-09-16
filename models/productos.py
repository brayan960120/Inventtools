import os
from xmlrpc.client import boolean
from flask_login import login_required
from flask_login import login_required
from werkzeug.utils import secure_filename
from flask import flash, redirect, url_for, render_template, request, session
from sqlalchemy import Boolean, Column, Integer, String, Float, ForeignKey
from sqlalchemy_serializer import SerializerMixin
from src.models import session, Base
from sqlalchemy import update
from src.models.categorias import Categorias
from src.models import session as db_session



class Productos(Base,SerializerMixin):
    __tablename__ = 'productos'
    id = Column(Integer, primary_key=True)
    descripcion = Column(String(300), nullable=False)
    valor_unitario = Column(Integer, nullable=False)
    unidad_medida = Column(String(3), nullable=False)
    cantida_stock = Column(Integer, nullable=False)
    categoria = Column(Integer, ForeignKey('categorias.id'), nullable=False)
    activo = Column(Boolean, default=True)
    imagen = Column(String, nullable=True)

    
    

    def __init__(self, descripcion, valor_unitario, unidad_medida, cantida_stock, categoria, activo=True, imagen=None):
        self.descripcion = descripcion
        self.valor_unitario = valor_unitario
        self.unidad_medida = unidad_medida
        self.cantida_stock = cantida_stock
        self.categoria = categoria
        self.activo = activo
        self.imagen = imagen

    def obtener_productos():
        productos = session.query(
            Productos,
            Categorias
        ).join(
            Categorias,
            Productos.categoria == Categorias.id
        ).filter(
            Productos.activo.is_(True)
        ).all()

        return productos


    
    def agregar_producto(producto):
        session.add(producto)
        session.commit()
        return producto

    from datetime import datetime
    from flask_login import login_required, current_user
    from src.models.movimientos import Movimientos

    @login_required
    def eliminar_producto(id):

        producto = session.get(Productos, id)

        if not producto:
            flash("El producto no existe.")
            return False

    # Crear movimiento de salida
        movimiento = Movimientos(
            usuario_id=current_user.id,
            producto_id=producto.id,
            cantida_stock=producto.cantida_stock,
            valor_unitario=producto.valor_unitario,
            tipo_de_movimiento="Salida",
            fecha=datetime.now(),
            activo=True
        )

    # Guardar movimiento
        session.add(movimiento)

    # Desactivar producto
        producto.activo = False

    # Guardar ambos cambios
        session.commit()

        print(
            "Salida registrada por:",
            current_user.id,
            current_user.nombre_completo
        )

        return producto


    def actualizar_producto(producto, id, imagen=None):

        producto_modificar = db_session.get(Productos, id)

        if producto_modificar is None:
            return None

        producto_modificar.descripcion = producto.descripcion
        producto_modificar.valor_unitario = producto.valor_unitario
        producto_modificar.unidad_medida = producto.unidad_medida
        producto_modificar.cantida_stock = producto.cantida_stock
        producto_modificar.categoria = producto.categoria
        producto_modificar.activo = producto.activo

        if imagen and imagen.filename:

            os.makedirs('static/uploads', exist_ok=True)

            nombre_archivo = secure_filename(imagen.filename)

            ruta = os.path.join(
                'static',
                'uploads',
                nombre_archivo
            )

            imagen.save(ruta)

            producto_modificar.imagen = nombre_archivo

        # NO hacer commit aquí
        return producto_modificar
  

    @classmethod
    def obtener_producto_por_id(cls, id):
        return session.query(cls).filter_by(id=id).first()
    
    def obtener_categorias_por_producto(id):
        productos = session.query(Productos).filter_by(categoria=id).all()
        return productos
    def comprar(id):
        producto = session.query(Productos).get(id)
        return producto

    
    
    
    """def comprar():
        producto = session.query(Productos).get(id)   
        return producto"""


    
    

    

    
    

    

    
    


    
    

    

    
    

    

    
    

    

    
    

    

    
    