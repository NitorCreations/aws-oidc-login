import login.oidc_authorizer
import pytest
import requests
from login import config
import time

try:
    # For Python 3.5 and later
    from urllib.parse import parse_qs
    from urllib.parse import urlparse
except ImportError:
    # Python 2.7
    from urlparse import parse_qs
    from urlparse import urlparse

login.config.CALLBACK_SERVER_TIMEOUT = 2


def test_oidc_flow(webbrowser_patched_ok, oidc_token_url_patched):
    login.oidc_authorizer.OidcAuthenticationCodeFlowAuthorizer.code_result = None
    auth = login.oidc_authorizer.OidcAuthenticationCodeFlowAuthorizer()
    assert auth.get_id_token() == "testtoken"
    # mock request for token and check correct params sent there


def test_oidc_flow_fails_to_get_code(webbrowser_patched_no_code, oidc_token_url_patched):
    login.oidc_authorizer.OidcAuthenticationCodeFlowAuthorizer.code_result = None
    auth = login.oidc_authorizer.OidcAuthenticationCodeFlowAuthorizer()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        auth.get_id_token()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_oidc_flow_fails_wrong_state(webbrowser_patched_wrong_state, oidc_token_url_patched):
    login.oidc_authorizer.OidcAuthenticationCodeFlowAuthorizer.code_result = None
    auth = login.oidc_authorizer.OidcAuthenticationCodeFlowAuthorizer()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        auth.get_id_token()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


def test_oidc_flow_error_from_idp(webbrowser_patched_error_from_idp, oidc_token_url_patched):
    login.oidc_authorizer.OidcAuthenticationCodeFlowAuthorizer.code_result = None
    auth = login.oidc_authorizer.OidcAuthenticationCodeFlowAuthorizer()
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        auth.get_id_token()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1


@pytest.fixture(autouse=True)
def config_patched(mocker):
    mocker.patch('login.config.init', return_value=None)
    config.AUTHORITY_URL = 'https://test-authority'


@pytest.fixture
def webbrowser_patched_ok(monkeypatch):
    import webbrowser

    def _mock_webbrowser_open_new_ok(url):
        import time
        from threading import Thread
        query_components = parse_qs(urlparse(url).query)
        assert query_components['response_type'][0] == 'code'
        assert query_components['response_mode'][0] == 'query'
        assert 'http://localhost' in query_components['redirect_uri'][0]
        assert 'state' in query_components

        def callback():
            time.sleep(1)
            resp = requests.get(query_components['redirect_uri'][0] +
                                '?code=testcode&state=' + query_components['state'][0])
            assert resp.status_code == 200
            assert "done" in resp.text

        thread = Thread(target=callback)
        thread.start()

    monkeypatch.setattr(webbrowser, 'open_new', _mock_webbrowser_open_new_ok)


@pytest.fixture
def oidc_token_url_patched(requests_mock):

    def match_code(request):
        assert "code=testcode" in (request.text or ""), "Expecting code parameter with value 'testcode'"
        return "code=testcode" in (request.text or "")

    requests_mock.post(config.AUTHORITY_URL + '/token', additional_matcher=match_code, text='{"id_token": "testtoken"}')
    requests_mock.get('http://localhost:8401', real_http=True)


@pytest.fixture
def webbrowser_patched_wrong_state(monkeypatch):
    import webbrowser

    def _mock_webbrowser_open_new_wrong_state(url):
        import time
        from threading import Thread
        query_components = parse_qs(urlparse(url).query)
        assert 'http://localhost' in query_components['redirect_uri'][0]

        def callback():
            time.sleep(1)
            resp = requests.get(query_components['redirect_uri'][0] + '?code=testcode&state=' +
                                query_components['state'][0] + "wrong")
            assert resp.status_code == 400
            assert "state" in resp.text

        thread = Thread(target=callback)
        thread.start()

    monkeypatch.setattr(webbrowser, 'open_new', _mock_webbrowser_open_new_wrong_state)


@pytest.fixture
def webbrowser_patched_no_code(monkeypatch):
    import webbrowser

    def _mock_webbrowser_open_new_no_code(url):
        from threading import Thread
        query_components = parse_qs(urlparse(url).query)
        assert 'http://localhost' in query_components['redirect_uri'][0]

        def callback():
            time.sleep(1)
            resp = requests.get(query_components['redirect_uri'][0])
            assert resp.status_code == 400
            assert "code" in resp.text

        thread = Thread(target=callback)
        thread.start()

    monkeypatch.setattr(webbrowser, 'open_new', _mock_webbrowser_open_new_no_code)


@pytest.fixture
def webbrowser_patched_error_from_idp(monkeypatch):
    import webbrowser

    def _mock_webbrowser_open_new_error_from_idp(url):
        import time
        from threading import Thread
        query_components = parse_qs(urlparse(url).query)
        assert query_components['response_type'][0] == 'code'
        assert query_components['response_mode'][0] == 'query'
        assert 'http://localhost' in query_components['redirect_uri'][0]
        assert 'state' in query_components

        def callback():
            time.sleep(1)
            resp = requests.get(query_components['redirect_uri'][0] +
                                '?error=errorfromidp&state=' + query_components['state'][0])
            assert resp.status_code == 400
            assert "An error occured" in resp.text

        thread = Thread(target=callback)
        thread.start()

    monkeypatch.setattr(webbrowser, 'open_new', _mock_webbrowser_open_new_error_from_idp)
