from src.models import Base, engine
from flask_controller import FlaskControllerRegister
from flask_login import LoginManager
from src.models.usuarios import Usuarios
from flask import Flask
from flask_cors import CORS
from flask_mail import Message
from src.mail import mail
from itsdangerous import URLSafeTimedSerializer


# ==================================================
# CREAR APLICACIÓN
# ==================================================

app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/static"
)


# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================

app.secret_key = "mi llaveria"
app.debug = True


# ==================================================
# CORS
# ==================================================

CORS(app)

app.config["CORS_HEADERS"] = "Content-Type"


# ==================================================
# CORREO
# ==================================================

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "dealtgow@gmail.com"
app.config["MAIL_PASSWORD"] = "TU_APP_PASSWORD"

mail.init_app(app)


# ==================================================
# FLASK CONTROLLERS
# ==================================================

register = FlaskControllerRegister(app)

register.register_package(
    "src.controllers"
)


# ==================================================
# BASE DE DATOS
# ==================================================

Base.metadata.create_all(engine)


# ==================================================
# FLASK-LOGIN
# ==================================================

login_manager = LoginManager()

login_manager.init_app(app)

# Tu función de login se llama "login"
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(id_usuario):

    return Usuarios.obtener_usuario_por_id(
        int(id_usuario)
    )


# ==================================================
# GENERAR TOKEN
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
# PRUEBA DE CORREO
# ==================================================

@app.route("/test-mail")
def test_mail():

    mensaje = Message(
        subject="Prueba desde Flask",
        sender=app.config["MAIL_USERNAME"],
        recipients=[
            "bhjuolp@gmail.com"
        ]
    )

    mensaje.body = (
        "Este correo fue enviado "
        "desde mi aplicación Flask."
    )

    mail.send(mensaje)

    return "Correo enviado correctamente"


# ==================================================
# EJECUTAR APLICACIÓN
# ==================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
