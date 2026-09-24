from flask import render_template
from flask_login import login_required
from sqlalchemy import func

from src.app import app
from src.models import session
from src.models.productos import Productos
from src.models.movimientos import Movimientos


@app.route("/dashboard")
@login_required
def dashboard():

    # ==========================================
    # TOTAL DE PRODUCTOS ACTIVOS
    # ==========================================

    total_productos = (
        session.query(func.count(Productos.id))
        .filter(Productos.activo.is_(True))
        .scalar()
        or 0
    )

    # ==========================================
    # STOCK TOTAL
    # ==========================================

    total_stock = (
        session.query(
            func.coalesce(
                func.sum(Productos.cantida_stock),
                0
            )
        )
        .filter(Productos.activo.is_(True))
        .scalar()
        or 0
    )

    # ==========================================
    # TOTAL ENTRADAS
    # ==========================================

    total_entradas = (
        session.query(
            func.coalesce(
                func.sum(Movimientos.cantida_stock),
                0
            )
        )
        .filter(
            Movimientos.tipo_de_movimiento == "Entrada",
            Movimientos.activo.is_(True)
        )
        .scalar()
        or 0
    )

    # ==========================================
    # TOTAL SALIDAS
    # ==========================================

    total_salidas = (
        session.query(
            func.coalesce(
                func.sum(Movimientos.cantida_stock),
                0
            )
        )
        .filter(
            Movimientos.tipo_de_movimiento == "Salida",
            Movimientos.activo.is_(True)
        )
        .scalar()
        or 0
    )

    # ==========================================
    # MOVIMIENTOS RECIENTES
    # ==========================================

    movimientos_recientes = (
        session.query(Movimientos)
        .join(
            Productos,
            Movimientos.producto_id == Productos.id
        )
        .filter(
            Movimientos.activo.is_(True)
        )
        .order_by(
            Movimientos.fecha.desc()
        )
        .limit(5)
        .all()
    )

    # ==========================================
    # PRODUCTOS CON STOCK BAJO
    # ==========================================

    productos_stock_bajo = (
        session.query(Productos)
        .filter(
            Productos.activo.is_(True),
            Productos.cantida_stock <= 5
        )
        .count()
    )

    # ==========================================
    # PORCENTAJE VISUAL
    # ==========================================

    stock_maximo_producto = (
        session.query(
            func.max(Productos.cantida_stock)
        )
        .filter(
            Productos.activo.is_(True)
        )
        .scalar()
        or 0
    )

    if total_productos > 0 and stock_maximo_producto > 0:

        capacidad_referencia = (
            stock_maximo_producto * total_productos
        )

        stock_porcentaje = round(
            (total_stock / capacidad_referencia) * 100
        )

        stock_porcentaje = max(
            0,
            min(stock_porcentaje, 100)
        )

    else:

        stock_porcentaje = 0

    return render_template(
        "dashboard.html",
        total_productos=total_productos,
        total_stock=total_stock,
        total_entradas=total_entradas,
        total_salidas=total_salidas,
        movimientos_recientes=movimientos_recientes,
        productos_stock_bajo=productos_stock_bajo,
        stock_porcentaje=stock_porcentaje
    )
