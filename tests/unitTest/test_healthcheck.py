"""
import pytest
from flask import Flask
from controller.service_controller import bp

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    app.config["TESTING"] = True
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_healthcheck(client):
    response = client.get("/healthcheck")
    assert response.status_code == 200, "Se esperaba status 200"
    assert response.get_json() == {"status": "ok"}, "La respuesta debe ser {'status': 'ok'}"
"""