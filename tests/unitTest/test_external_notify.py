"""
from externals.notify_service import send_notification
from unittest.mock import patch


def test_succes_notification_return_true():
    with patch("requests.post") as mock_post:
        mock_post.return_value.status_code = 200
        result = send_notification("1234567890", "123456", "sms")
        assert result is True

"""