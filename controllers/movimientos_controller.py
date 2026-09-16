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


        
@app.route("/movimientos")
def movimientos():
    movimientos = (
        session.query(Movimientos)
        .join(Usuarios, Movimientos.usuario_id == Usuarios.id)
        .join(Productos, Movimientos.producto_id == Productos.id)
        .order_by(Movimientos.fecha.asc())
        .all()
    )
    return render_template(
        "tabla_movimientos.html",
        movimientos=movimientos
    )

@app.route("/movimientos/agregar_movimiento", methods=["GET", "POST"])
def agregar_movimiento():

    usuarios = session.query(Usuarios).all()
    productos = session.query(Productos).all()

    if request.method == "POST":

        movimiento = Movimientos(
            usuario_id=request.form["usuario_id"],
            producto_id=request.form["producto_id"],
            cantida_stock=request.form["cantida_stock"],
            valor_unitario=request.form["valor_unitario"],
            tipo_de_movimiento="Entrada",
            fecha=datetime.datetime.now(),
            activo=True
        )

        print("========== NUEVO MOVIMIENTO ==========")
        print("Usuario:", movimiento.usuario_id)
        print("Producto:", movimiento.producto_id)
        print("Cantidad:", movimiento.cantida_stock)
        print("Tipo:", movimiento.tipo_de_movimiento)
        print("======================================")

        session.add(movimiento)
        session.commit()

        return redirect(url_for("movimientos"))

    return render_template(
        "formulario_crear_movimiento.html",
        usuarios=usuarios,
        productos=productos,
        tipo="Entrada"
    )

