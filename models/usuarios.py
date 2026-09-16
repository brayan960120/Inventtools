from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask import flash
from src.models import session, Base
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2



class Usuarios(Base, UserMixin):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True)
    nombre_completo = Column(String(200))
    email = Column(String(500), unique=True, nullable=False)
    contraseña = Column(String(30), nullable=False)
    rol = Column(String(30), nullable=False)
    movimientos = relationship(
        'Movimientos',
        back_populates='usuario'
    )
    

   

    def __init__(self, nombre_completo, email, contraseña, rol):
        self.nombre_completo = nombre_completo
        self.email = email
        self.contraseña = contraseña
        self.rol = rol
        

    def obtener_usuarios():
        usuarios = session.query(Usuarios).all()
        return usuarios
    
    def agregar_usuario(usuario):
        usuario = session.add(usuario)
        session.commit()
        return usuario
    
    def eliminar_usuario(id):

        from src.models.movimientos import Movimientos

        usuario = session.query(Usuarios).get(id)

        if not usuario:
            flash("El usuario no existe.")
            return False

        movimientos = (
            session.query(Movimientos)
            .filter(Movimientos.usuario_id == id)
            .first()
        )

        if movimientos:
            flash(
                "No se puede eliminar el usuario porque tiene movimientos registrados."
            )
            return False

        session.delete(usuario)
        session.commit()

        return usuario

       
    def validar_usuario(email, contraseña):
        usuario_valido = session.query(Usuarios).filter_by(email=email).first()
        if usuario_valido:
            if usuario_valido.contraseña == contraseña:
                return usuario_valido
        return False
        
    def obtener_usuario_por_id(id):
        usuario = session.query(Usuarios).get(id)
        return usuario
    
    def actualizar_usuario(usuario,id):
        
        usuario_modificar = session.query(Usuarios).get(id)
        

    
        usuario_modificar.nombre_completo = usuario.nombre_completo
        usuario_modificar.email = usuario.email
        usuario_modificar.contraseña = usuario.contraseña
        usuario_modificar.rol = usuario.rol
        session.commit()      
        return usuario
   
    
    def email_existe(email):
        usuario = session.query(Usuarios).filter(Usuarios.email == email).first()
        return usuario
    