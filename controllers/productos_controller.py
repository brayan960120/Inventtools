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
from sqlalchemy import or_


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

        buscar = request.args.get('buscar', '').strip()

        productos = Productos.obtener_productos(buscar)

        return render_template(
            'tabla_productos.html',
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


    @app.route('/actualizar_producto/<int:id>', methods=['GET', 'POST'])
    @login_required
    def actualizar_producto(id):

        if 'email' not in session:
            return redirect(url_for('login'))

        usuario = db_session.query(
            Usuarios
        ).filter_by(
            email=session['email']
        ).first()

        if usuario is None:
            flash("No se encontró el usuario.", "danger")
            return redirect(url_for('login'))

        producto = db_session.get(Productos, id)

        if producto is None:
            flash("El producto no existe.", "danger")
            return redirect(url_for('ver_productos'))

    # ============================
    # GET
    # ============================

        if request.method == 'GET':

            categorias = Categorias.obtener_categorias()

            return render_template(
                'formulario_actualizar_producto.html',
                titulo_pagina='Actualizar Producto',
                producto=producto,
                categoria=categorias,
                tipo_de_movimiento='actualizar'
            )

    # ============================
    # POST
    # ============================

        descripcion = request.form.get(
            'descripcion',
            ''
        ).strip()

        valor_unitario = request.form.get(
            'valor_unitario',
            ''
        ).strip()

        unidad_medida = request.form.get(
            'unidad_medida',
            ''
        ).strip()

        cantida_stock = request.form.get(
            'cantida_stock',
            ''
        ).strip()

        categoria = request.form.get(
            'categoria',
            ''
        ).strip()

    # ============================
    # VALIDACIONES
    # ============================

        if not descripcion:
            flash("La descripción es obligatoria.", "danger")
            return redirect(
                url_for('actualizar_producto', id=id)
            )

        if not valor_unitario:
            flash("El valor unitario es obligatorio.", "danger")
            return redirect(
                url_for('actualizar_producto', id=id)
            )

        if not unidad_medida:
            flash("La unidad de medida es obligatoria.", "danger")
            return redirect(
                url_for('actualizar_producto', id=id)
            )

        if not cantida_stock:
            flash("La cantidad en stock es obligatoria.", "danger")
            return redirect(
                url_for('actualizar_producto', id=id)
            )

        if not categoria:
            flash("La categoría es obligatoria.", "danger")
            return redirect(
                url_for('actualizar_producto', id=id)
            )

    # ============================
    # CONVERTIR VALORES
    # ============================

        try:

            stock_nuevo = int(cantida_stock)

            precio_nuevo = float(
                valor_unitario.replace(',', '.')
            )

            categoria_nueva = int(categoria)

        except ValueError:

            flash(
                "Los valores ingresados no son válidos.",
                "danger"
            )

            return redirect(
                url_for('actualizar_producto', id=id)
            )

        if stock_nuevo < 0:

            flash(
                "El stock no puede ser negativo.",
                "danger"
            )

            return redirect(
                url_for('actualizar_producto', id=id)
            )

    # ============================
    # STOCK ANTERIOR
    # ============================

        stock_anterior = producto.cantida_stock

    # Diferencia:
    # + = entrada
    # - = salida

        diferencia_stock = (
            stock_nuevo - stock_anterior
        )

    # ============================
    # IMAGEN
    # ============================

        imagen = request.files.get('imagen')

    # ============================
    # ACTUALIZAR PRODUCTO
    # ============================

        producto.descripcion = descripcion
        producto.valor_unitario = precio_nuevo
        producto.unidad_medida = unidad_medida
        producto.cantida_stock = stock_nuevo
        producto.categoria = categoria_nueva

    # ============================
    # ACTIVO / INACTIVO
    # ============================

        producto.activo = stock_nuevo > 0

    # ============================
    # IMAGEN
    # ============================

        if imagen and imagen.filename:

            os.makedirs(
                'static/uploads',
                exist_ok=True
            )

            nombre_archivo = secure_filename(
                imagen.filename
            )

            ruta = os.path.join(
                'static',
                'uploads',
                nombre_archivo
            )

            imagen.save(ruta)

            producto.imagen = nombre_archivo

    # ============================
    # REGISTRAR MOVIMIENTO
    # ============================

        if diferencia_stock != 0:

            if diferencia_stock > 0:

                tipo_movimiento = "Entrada"
                cantidad_movimiento = diferencia_stock

            else:

                tipo_movimiento = "Salida"
                cantidad_movimiento = abs(
                    diferencia_stock
                )

            movimiento = Movimientos(
                usuario_id=usuario.id,
                producto_id=producto.id,
                cantida_stock=cantidad_movimiento,
                valor_unitario=precio_nuevo,
                tipo_de_movimiento=tipo_movimiento,
                fecha=datetime.datetime.now(),
                activo=True
            )

            db_session.add(movimiento)

    # ============================
    # GUARDAR
    # ============================

        try:

            db_session.commit()

            if diferencia_stock > 0:

                flash(
                    f"Producto actualizado. "
                    f"Se registró una entrada de "
                    f"{diferencia_stock} unidades.",
                    "success"
                )

            elif diferencia_stock < 0:

                flash(
                    f"Producto actualizado. "
                    f"Se registró una salida de "
                    f"{abs(diferencia_stock)} unidades.",
                    "success"
                )

            else:

                flash(
                    "Producto actualizado correctamente.",
                    "success"
                )

        except Exception as e:

            db_session.rollback()

            print(
                "ERROR ACTUALIZANDO PRODUCTO:",
                e
            )

            flash(
                "No fue posible actualizar el producto.",
                "danger"
            )

        return redirect(
            url_for('ver_productos')
        )
    

    @app.route('/cambiar_estado_producto/<int:id>', methods=['POST'])
    def cambiar_estado_producto(id):

        producto = db_session.get(Productos, id)

        if producto is None:
            flash('Producto no encontrado.')
            return redirect(url_for('ver_productos'))

        # Si el checkbox está marcado, Flask recibe "1"
        activo = request.form.get('activo')

        # ACTIVAR
        if activo == '1':

            # Verificar el stock actual
            if producto.cantida_stock > 0:

                producto.activo = True

                flash('Producto activado correctamente.')

            else:

                producto.activo = False

                flash('No se puede activar el producto porque no tiene stock.')

        # DESACTIVAR
        else:

            producto.activo = False

            flash('Producto desactivado correctamente.')

        db_session.commit()

        return redirect(url_for('ver_productos'))

    











        
   
    
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