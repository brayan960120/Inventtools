from flask import render_template, session
from src.app import app

from sqlalchemy import func

from src.models import session as db_session
from src.models.productos import Productos
from src.models.movimientos import Movimientos


@app.route("/")
def index():

    # ==========================================
    # TOTAL PRODUCTOS ACTIVOS
    # ==========================================

    total_productos = (
        db_session.query(
            func.count(Productos.id)
        )
        .filter(
            Productos.activo.is_(True)
        )
        .scalar()
        or 0
    )


    # ==========================================
    # STOCK TOTAL
    # ==========================================

    total_stock = (
        db_session.query(
            func.coalesce(
                func.sum(Productos.cantida_stock),
                0
            )
        )
        .filter(
            Productos.activo.is_(True)
        )
        .scalar()
        or 0
    )


    # ==========================================
    # TOTAL ENTRADAS
    # ==========================================

    total_entradas = (
        db_session.query(
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
        db_session.query(
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
        db_session.query(Movimientos)
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
        db_session.query(Productos)
        .filter(
            Productos.activo.is_(True),
            Productos.cantida_stock <= 5
        )
        .count()
    )


    # ==========================================
    # PORCENTAJE DE STOCK
    # ==========================================

    stock_maximo_producto = (
        db_session.query(
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


    # ==========================================
    # INDEX
    # ==========================================

    return render_template(
        "index.html",

        titulo_pagina="Inicio",

        email=session.get("email"),

        total_productos=total_productos,

        total_stock=total_stock,

        total_entradas=total_entradas,

        total_salidas=total_salidas,

        movimientos_recientes=movimientos_recientes,

        productos_stock_bajo=productos_stock_bajo,

        stock_porcentaje=stock_porcentaje
    )