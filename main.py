from flask import Flask
from controller.service_controller import bp

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == "__main__":
    port = 8080
    print(f"Servidor escuchando en el puerto {port}")
    try:
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
