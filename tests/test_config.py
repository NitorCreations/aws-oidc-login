import login.config as config
import pytest
import argparse

try:
    # For Python 3.5 and later
    import configparser
except ImportError:
    # Fall back to Python 2
    import ConfigParser as configparser  # noqa: F401

args = {"profile": "test-profile",
        "web_console_login": False}

params = {"oidc_role_arn": "arn:aws:iam::123456789012:role/test_role",
          "oidc_client_id": "testclientid",
          "oidc_authority_url": "https://testauthority"}

sections = {"profile test-profile": params}


def test_init_no_profile_found(args_patched):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        config.init()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    assert args_patched.call_count == 1


def test_init(args_patched, aws_config_patched):
    config.init()
    for mock in aws_config_patched:
        mock.call_count == 1
    args_patched.call_count == 1
    _verify_config(args, params)


def test_init_missing_authority_url(args_patched, aws_config_patched_without_authority_url):
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        config.init()
    assert pytest_wrapped_e.type == SystemExit
    assert pytest_wrapped_e.value.code == 1
    for mock in aws_config_patched_without_authority_url:
        mock.call_count == 1
    args_patched.call_count == 1


def _verify_config(args, params):
    assert config.PROFILE == args['profile']
    assert config.CONFIG_PROFILE == "profile {}".format(args['profile'])
    assert config.ROLE_ARN == params['oidc_role_arn']
    assert config.CLIENT_ID == params['oidc_client_id']
    assert config.AUTHORITY_URL == params['oidc_authority_url']
    assert config.WEB_CONSOLE_LOGIN == args['web_console_login']


@pytest.fixture
def args_patched(mocker):
    return mocker.patch('argparse.ArgumentParser.parse_args', return_value=argparse.Namespace(**args))


@pytest.fixture
def aws_config_patched(mocker):
    mock1 = mocker.patch('configparser.ConfigParser.__getitem__', return_value=params)
    mock2 = mocker.patch('configparser.ConfigParser.read', return_value=None)
    mock3 = mocker.patch('configparser.ConfigParser.has_section', return_value=True)
    return mock1, mock2, mock3


@pytest.fixture
def aws_config_patched_without_authority_url(mocker):
    newparams = params.copy()
    newparams.pop("oidc_authority_url")
    mock1 = mocker.patch('configparser.ConfigParser.__getitem__', return_value=newparams)
    mock2 = mocker.patch('configparser.ConfigParser.read', return_value=None)
    mock3 = mocker.patch('configparser.ConfigParser.has_section', return_value=True)
    return mock1, mock2, mock3
