import login.aws_oidc_login
import pytest
import login.config as config
from datetime import datetime

test_role_arn = "arn:aws:iam::123456789012:role/test_role"
test_email = "test@nitor.com"
test_profile = 'default'
assume_role_response = {'Credentials':
                        {'AccessKeyId': 'testkeytestkeytestkey',
                         'SecretAccessKey': 'testsecret',
                         'SessionToken': 'testtoken',
                         'Expiration': datetime.now()}}


def test_web_console_login(requests_mock):
    requests_mock.get("https://signin.aws.amazon.com/federation", text='{"SigninToken": "testtoken"}')

    web_console_url = login.aws_oidc_login.web_console_login(assume_role_response)

    assert "SigninToken=testtoken" in web_console_url


def _mock_token(self):
    import tests.test_jwt
    return tests.test_jwt.get_test_jwt(email=test_email)


@pytest.fixture
def oidc_patched(monkeypatch):
    from login.oidc_authorizer import OidcAuthenticationCodeFlowAuthorizer
    monkeypatch.setattr(OidcAuthenticationCodeFlowAuthorizer, 'get_id_token', _mock_token)


def _mock_assume_role_with_web_identity(RoleArn, RoleSessionName, WebIdentityToken, DurationSeconds):
    role = {'Credentials': {'AccessKeyId': 'testkeytestkeytestkey',
                            'SecretAccessKey': 'testsecret', 'SessionToken': 'testtoken'}}
    return role


@pytest.fixture
def aws_federation_endpoint_patched(requests_mock):
    requests_mock.get("https://signin.aws.amazon.com/federation", text='{"SigninToken": "testtoken"}')


@pytest.fixture(autouse=True)
def sts_stub():
    from login.aws_oidc_login import aws_sts
    from botocore.stub import Stubber

    with Stubber(aws_sts) as stubber:
        yield stubber
        stubber.assert_no_pending_responses()


@pytest.fixture
def config_patched(mocker):
    mocker.patch('login.config.init', return_value=None)
    config.ROLE_ARN = test_role_arn
    config.PROFILE = test_profile


@pytest.fixture
def credentials_patched(mocker):
    return mocker.patch('login.credentials.write', return_value=None)


def test_login(oidc_patched, aws_federation_endpoint_patched, sts_stub, config_patched, credentials_patched):
    import tests.test_jwt

    expected_params = {'RoleArn': test_role_arn, 'RoleSessionName': test_email,
                       'WebIdentityToken': tests.test_jwt.get_test_jwt(),
                       'DurationSeconds': 3600}
    sts_stub.add_response('assume_role_with_web_identity', assume_role_response, expected_params)

    login.aws_oidc_login.aws_oidc_login()

    credentials_patched.assert_called_with(assume_role_response)
