import datetime

from flask_login import current_user, login_required
from src.app import app
from flask import render_template, request, redirect, url_for, flash
from flask_controller import FlaskController
from src.models.productos import Productos
from src.models.categorias import Categorias
from src.models.usuarios import Usuarios
from src.models.detalle_facturas import DetalleFacturas
from src.models.movimientos import Movimientos
from src.models import session

from src.models import session


@app.route('/movimientos')
@login_required
def ver_movimientos():

    movimientos = session.query(
        Movimientos
    ).order_by(
        Movimientos.fecha.desc()
    ).all()

    return render_template(
    'tabla_movimientos.html',
    movimientos=movimientos
)



@app.route(
    "/movimientos/agregar_movimiento",
    methods=["GET", "POST"]
)
@login_required
def agregar_movimiento():

    usuarios = session.query(Usuarios).all()

    productos = (
        session.query(Productos)
        .filter(Productos.activo.is_(True))
        .all()
    )

    if request.method == "POST":

        try:

            usuario_id = int(
                request.form["usuario_id"]
            )

            producto_id = int(
                request.form["producto_id"]
            )

            cantidad = int(
                request.form["cantida_stock"]
            )

            valor_unitario = float(
                request.form["valor_unitario"]
            )

            tipo = request.form.get(
                "tipo_de_movimiento",
                "Entrada"
            )

            if cantidad <= 0:

                flash(
                    "La cantidad debe ser mayor que cero.",
                    "danger"
                )

                return redirect(
                    url_for("agregar_movimiento")
                )

            producto = session.get(
                Productos,
                producto_id
            )

            if producto is None:

                flash(
                    "El producto no existe.",
                    "danger"
                )

                return redirect(
                    url_for("agregar_movimiento")
                )

            # ==========================================
            # ENTRADA
            # ==========================================

            if tipo == "Entrada":

                producto.cantida_stock += cantidad

                producto.activo = True

            # ==========================================
            # SALIDA
            # ==========================================

            elif tipo == "Salida":

                if producto.cantida_stock < cantidad:

                    flash(
                        "No hay suficiente stock disponible.",
                        "danger"
                    )

                    return redirect(
                        url_for("agregar_movimiento")
                    )

                producto.cantida_stock -= cantidad

                if producto.cantida_stock == 0:

                    producto.activo = False

            else:

                flash(
                    "Tipo de movimiento inválido.",
                    "danger"
                )

                return redirect(
                    url_for("agregar_movimiento")
                )

            # ==========================================
            # CREAR MOVIMIENTO
            # ==========================================

            movimiento = Movimientos(

                usuario_id=usuario_id,

                producto_id=producto_id,

                cantida_stock=cantidad,

                valor_unitario=valor_unitario,

                tipo_de_movimiento=tipo,

                fecha=datetime.datetime.now(),

                activo=True
            )

            session.add(movimiento)

            session.commit()

            flash(
                "Movimiento registrado correctamente.",
                "success"
            )

            return redirect(
                url_for("ver_movimientos")
            )

        except Exception as e:

            session.rollback()

            print(
                "ERROR CREANDO MOVIMIENTO:",
                e
            )

            flash(
                "No fue posible registrar el movimiento.",
                "danger"
            )

            return redirect(
                url_for("agregar_movimiento")
            )

    return render_template(
        "formulario_crear_movimiento.html",
        usuarios=usuarios,
        productos=productos,
        tipo="Entrada"
    )



@app.route(
    '/actualizar_movimiento/<int:id>',
    methods=['GET', 'POST']
)
@login_required
def actualizar_movimiento(id):

    movimiento = session.get(
        Movimientos,
        id
    )

    # ...

        
