import datetime
from sqlalchemy import select
from sqlalchemy import false, true
from src.models import session, Base
from sqlalchemy import Column, Integer, String, Float, ForeignKey,true
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from src.models.movimientos import Movimientos
from src.app import app
from flask import render_template, request, redirect, url_for, flash,session
from flask_controller import FlaskController
from src.models.productos import Productos
from src.models.categorias import Categorias
from src.models.usuarios import Usuarios
from src.models.detalle_facturas import DetalleFacturas
from flask import session as flask_session
from src.models import session as db_session
import os
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user


class ProductosController(FlaskController):


    @app.route('/crear_producto', methods=['POST', 'GET'])
    def crear_producto():

        if 'email' not in session:
            return render_template('formulario_login.html')

        usuario = db_session.query(Usuarios).filter_by(
            email=session["email"]
        ).first()

        if request.method == 'POST':

            descripcion = request.form.get('descripcion')
            valor_unitario = request.form.get('valor_unitario')
            unidad_medida = request.form.get('unidad_medida')
            cantida_stock = request.form.get('cantida_stock')
            categoria = request.form.get('categoria')

        # Obtener imagen
            imagen = request.files.get('imagen')

        # Validaciones
            if not descripcion:
                flash('La descripción es obligatoria.', 'danger')

            if not valor_unitario:
                flash('El valor unitario es obligatorio.', 'danger')

            if not unidad_medida:
                flash('La unidad de medida es obligatoria.', 'danger')

            if not cantida_stock:
                flash('La cantidad en stock es obligatoria.', 'danger')

            if not categoria:
                flash('La categoría es obligatoria.', 'danger')

            if not all([
                descripcion,
                valor_unitario,
                unidad_medida,
                cantida_stock,
                categoria
            ]):
                return redirect(url_for('crear_producto'))

        # ---------------------------------
        # GUARDAR PRODUCTO
        # ---------------------------------

            producto = Productos(
                descripcion,
                valor_unitario,
                unidad_medida,
                cantida_stock,
                categoria,
                True
            )

        # ---------------------------------
        # GUARDAR IMAGEN SI EXISTE
        # ---------------------------------

            if imagen and imagen.filename:

            # Crear carpeta si no existe
                os.makedirs('static/uploads', exist_ok=True)

            # Limpiar nombre del archivo
                nombre_archivo = secure_filename(imagen.filename)

            # Ruta donde se guardará
                ruta = os.path.join(
                    'static',
                    'uploads',
                    nombre_archivo
                )

            # Guardar archivo
                imagen.save(ruta)

            # Guardar nombre en el producto
                producto.imagen = nombre_archivo

        # ---------------------------------
        # GUARDAR EN BASE DE DATOS
        # ---------------------------------

            db_session.add(producto)
            db_session.flush()

            movimiento = Movimientos(
                usuario_id=usuario.id,
                producto_id=producto.id,
                cantida_stock=producto.cantida_stock,
                valor_unitario=producto.valor_unitario,
                tipo_de_movimiento='Entrada',
                activo=True
            )

            db_session.add(movimiento)

            db_session.commit()
            
            

            return redirect(url_for('ver_productos'))

        categoria = Categorias.obtener_categorias()

        return render_template(
            'formulario_crear_producto.html',
            titulo_pagina='Crear Producto',
            usuario=usuario,
            categoria=categoria
        )


    
    @app.route('/ver_productos')
    def ver_productos():

        buscar = request.args.get("buscar", "")

        consulta = (
            db_session.query(Productos, Categorias.categoria)
            .join(Categorias)
            .filter(Productos.activo == True)
        )

        if buscar:
            consulta = consulta.filter(
                Productos.descripcion.ilike(f"%{buscar}%")
            )

        productos = consulta.all()
 
        return render_template(
            'tabla_productos.html',
            titulo_pagina='Ver Productos',
            productos=productos
        )
    

    @app.route("/eliminar_producto/<int:id>", methods=["POST"])
    @login_required
    def eliminar_producto(id):

        producto = db_session.get(Productos, id)

        print("========== ELIMINAR PRODUCTO ==========")
        print("ID recibido:", id)
        print("Producto:", producto)
        print("Tipo:", type(producto))
        print("=======================================")

        if producto is None:
            flash("El producto no existe.")
            return redirect(url_for("ver_productos"))

        movimiento = Movimientos(
            usuario_id=current_user.id,
            producto_id=producto.id,
            cantida_stock=producto.cantida_stock,
            valor_unitario=producto.valor_unitario,
            tipo_de_movimiento="Salida",
            fecha=datetime.datetime.now(),
            activo=True
        )

        db_session.add(movimiento)

        producto.activo = False

        db_session.commit()

        flash(
            f"Producto '{producto.descripcion}' eliminado correctamente."
        )

        return redirect(url_for("ver_productos"))


    @app.route('/actualizar_producto/<id>', methods=['GET', 'POST'])
    @login_required
    def actualizar_producto(id):

        if 'email' not in session:
            return render_template(
                'formulario_login.html',
                titulo_pagina='Login'
            )

        # Buscar usuario que está realizando la actualización
        usuario = db_session.query(Usuarios).filter_by(
            email=session["email"]
        ).first()

        if request.method == 'GET':

            producto = Productos.obtener_producto_por_id(id)
            categoria = Categorias.obtener_categorias()

            return render_template(
                'formulario_actualizar_producto.html',
                titulo_pagina='Actualizar Productos',
                producto=producto,
                categoria=categoria,
                tipo_de_movimiento='actualizar'
            )

        if request.method == 'POST':

    # -----------------------------------------
    # BUSCAR PRODUCTO ACTUAL
    # -----------------------------------------

            producto_actual = db_session.get(Productos, id)

            if producto_actual is None:
                flash("El producto no existe.")
                return redirect(url_for("ver_productos"))

            # Guardamos los valores anteriores
            stock_anterior = producto_actual.cantida_stock
            precio_anterior = producto_actual.valor_unitario
            descripcion_anterior = producto_actual.descripcion
            unidad_anterior = producto_actual.unidad_medida
            categoria_anterior = producto_actual.categoria

        # -----------------------------------------
        # DATOS NUEVOS DEL FORMULARIO
        # -----------------------------------------

            descripcion = request.form.get('descripcion')
            valor_unitario = request.form.get('valor_unitario')
            unidad_medida = request.form.get('unidad_medida')
            cantida_stock = request.form.get('cantida_stock')
            categoria = request.form.get('categoria')

        # Convertir números
            stock_nuevo = int(cantida_stock)
            precio_nuevo = float(valor_unitario)

        # Imagen
            imagen = request.files.get('imagen')

        # -----------------------------------------
        # ACTUALIZAR PRODUCTO
        # -----------------------------------------

            producto_modificar = Productos(
                descripcion,
                precio_nuevo,
                unidad_medida,
                stock_nuevo,
                categoria,
                True
            )

            Productos.actualizar_producto(
                producto_modificar,
                id,
                imagen
            )

        # -----------------------------------------
        # DETERMINAR TIPO DE MOVIMIENTO
        # -----------------------------------------

            if stock_nuevo > stock_anterior:

                tipo_movimiento = "Entrada"

            elif stock_nuevo < stock_anterior:

                tipo_movimiento = "Salida"

            else:

                tipo_movimiento = "Actualización"

        # -----------------------------------------
        # CREAR MOVIMIENTO
        # -----------------------------------------

            movimiento = Movimientos(
                usuario_id=usuario.id,
                producto_id=id,
                cantida_stock=stock_nuevo,
                valor_unitario=precio_nuevo,
                tipo_de_movimiento=tipo_movimiento,
                fecha=datetime.datetime.now(),
                activo=True
            )

            db_session.add(movimiento)
            db_session.commit()

            flash(
                f"Producto '{descripcion}' actualizado correctamente."
            )

            return redirect(url_for("ver_productos"))


        
   
    
    @app.route('/comprar/<id>', methods=['GET', 'POST'])
    def comprar(id):
        if 'email' in session:
            if request.method == 'GET':
        # Lógica para mostrar el formulario de edición con los datos actuales del producto
                producto= Productos.obtener_producto_por_id(id)
                categoria = Categorias.obtener_categorias()
                return render_template('formulario_compras.html',titulo_pagina = 'Actualizar Productos', producto=producto, categoria=categoria)

            if request.method == 'POST':
                valor_unitario = request.form.get('precio_unitario')
                cantidad= request.form.get('cantidad') 
                valor_total = request.form.get('precio_total')       
                id_producto= request.form.get('id_producto')  
                id_usuario = request.form.get('id_usuario')
            
                compra = Compras(valor_unitario, cantidad,valor_total, id_producto, id_usuario)
                Compras.agregar_compras(compra,id_producto)
                return redirect(url_for('/comprar'))