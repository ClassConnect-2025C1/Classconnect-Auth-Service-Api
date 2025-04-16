""" 
import uuid
from unittest.mock import MagicMock, patch
from routes.auth import register
from schemas.auth_schemas import UserRegister
from models.credential_models import Credential

def test_register_success():
   
    fake_user = UserRegister(
        email="test@example.com",
        password="123456",
        name="Test",
        last_name="User",
        role="student"
    )

    
    mock_db = MagicMock()
    mock_db.query().filter().first.return_value = None  #

    # Patch del hash_password y create_access_token
    with patch("auth.routes.hash_password", return_value="hashed"), \
         patch("auth.routes.create_access_token", return_value="mocktoken"), \
         patch("auth.routes.httpx.post") as mock_post:

        # Simular que la respuesta del microservicio de profile fue exitosa
        mock_post.return_value.status_code = 200
        mock_post.return_value.raise_for_status.return_value = None

        response = register(fake_user, mock_db)

        assert response["access_token"] == "mocktoken"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_post.assert_called_once()
"""