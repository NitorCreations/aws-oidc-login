import pytest  # noqa F401
import login.jwt
from base64 import urlsafe_b64encode


def get_test_jwt(email="test@nitor.com"):
    token_parts = [urlsafe_b64encode('{}'.encode()).decode(),
                   urlsafe_b64encode('{{"email": "{EMAIL}"}}'.format(EMAIL=email).encode()).decode(),
                   urlsafe_b64encode('{}'.encode()).decode()]
    return '.'.join(token_parts)


def get_test_jwt_no_email():
    token_parts = [urlsafe_b64encode('{}'.encode()).decode(),
                   urlsafe_b64encode('{}'.encode()).decode(),
                   urlsafe_b64encode('{}'.encode()).decode()]
    return '.'.join(token_parts)


def test_parse_email_from_jwt():
    assert login.jwt.get_email(get_test_jwt()) == "test@nitor.com"


def test_parse_email_not_in_token():
    assert login.jwt.get_email(get_test_jwt_no_email()) == "no-email-in-oidc-token"
