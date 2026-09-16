from itsdangerous import URLSafeTimedSerializer

from flask_mail import Message

from src.app import app

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

from flask_controller import FlaskController

from src.models.usuarios import Usuarios
from src.models import session as db_session
from src.mail import mail

from flask_login import (
    login_user,
    logout_user
)


class LoginController(FlaskController):

    # ==================================================
    # LOGIN
    # ==================================================

    @app.route(
        "/login",
        methods=["GET", "POST"]
    )
    def login():

        if request.method == "POST":

            email = request.form.get("email")
            contraseña = request.form.get("contrasena")

            # Buscar usuario por email y contraseña
            usuario_valido = Usuarios.validar_usuario(
                email,
                contraseña
            )

            if usuario_valido:

                # ==========================================
                # FLASK-LOGIN
                # ==========================================

                login_user(usuario_valido)

                # ==========================================
                # MANTENER TU SESSION ACTUAL POR EMAIL
                # ==========================================

                session["email"] = email

                print(
                    "Usuario conectado:",
                    usuario_valido.id,
                    usuario_valido.nombre_completo
                )

                flash(
                    "Has iniciado sesión exitosamente"
                )

                return redirect(
                    url_for("index")
                )

            else:

                flash(
                    "El email o la contraseña son incorrectos"
                )

        return render_template(
            "formulario_login.html",
            titulo_pagina="login"
        )


# ==================================================
# GENERAR TOKEN PARA RECUPERAR CONTRASEÑA
# ==================================================

def generar_token(email):

    serializer = URLSafeTimedSerializer(
        app.secret_key
    )

    token = serializer.dumps(
        email,
        salt="recuperar-password"
    )

    return token


# ==================================================
# OLVIDÉ MI CONTRASEÑA
# ==================================================

@app.route(
    "/olvidar-password",
    methods=["GET", "POST"]
)
def olvidar_password():

    if request.method == "POST":

        email = request.form.get("email")

        usuario = Usuarios.email_existe(email)

        if usuario:

            token = generar_token(email)

            enlace = url_for(
                "restablecer_password",
                token=token,
                _external=True
            )

            mensaje = Message(
                subject="Recuperar contraseña - Inventtools",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email]
            )

            mensaje.body = f"""
Hola {usuario.nombre_completo}.

Recibimos una solicitud para cambiar tu contraseña.

Haz clic en el siguiente enlace:

{enlace}

Este enlace es válido durante 1 hora.

Si tú no solicitaste este cambio, ignora este correo.
"""

            mail.send(mensaje)

        # No revelar si el correo existe o no
        flash(
            "Si el correo está registrado, "
            "recibirás un enlace."
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "olvidar_password.html",
        titulo_pagina="Recuperar contraseña"
    )


# ==================================================
# RESTABLECER CONTRASEÑA
# ==================================================

@app.route(
    "/restablecer-password/<token>",
    methods=["GET", "POST"]
)
def restablecer_password(token):

    serializer = URLSafeTimedSerializer(
        app.secret_key
    )

    try:

        email = serializer.loads(
            token,
            salt="recuperar-password",
            max_age=3600
        )

    except Exception:

        flash(
            "El enlace es inválido o ha expirado."
        )

        return redirect(
            url_for("login")
        )

    usuario = Usuarios.email_existe(email)

    if not usuario:

        flash(
            "Usuario no encontrado."
        )

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        password = request.form.get("password")
        confirmar_password = request.form.get(
            "confirmar_password"
        )

        if password != confirmar_password:

            flash(
                "Las contraseñas no coinciden."
            )

            return render_template(
                "restablecer_password.html"
            )

        # Actualizar contraseña
        usuario.contraseña = password

        db_session.commit()

        flash(
            "Contraseña actualizada correctamente."
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "restablecer_password.html"
    )


# ==================================================
# CERRAR SESIÓN
# ==================================================

@app.route("/logout")
def logout():

    # Cerrar sesión de Flask-Login
    logout_user()

    # Mantener compatibilidad con tu sesión actual
    session.pop("email", None)

    flash(
        "Has salido exitosamente."
    )

    return redirect(
        url_for("login")
    )
