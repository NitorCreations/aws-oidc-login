
from os.path import expanduser
import sys
import argparse

try:
    # For Python 3.5 and later
    import configparser
except ImportError:
    # Fall back to Python 2
    import ConfigParser as configparser  # noqa: F401


AUTH_SCOPE = ('openid email')
CALLBACK_SERVER_TIMEOUT = 30
CLIENT_ID = None
AUTHORITY_URL = None
ROLE_ARN = None
PROFILE = None
CONFIG_PROFILE = None
WEB_CONSOLE_LOGIN = False
PRINT_AUTHORIZE_URL = False


def init():
    global CLIENT_ID, AUTHORITY_URL, ROLE_ARN, PROFILE, CONFIG_PROFILE
    _init_from_args(_parse_args())
    aws_config = configparser.ConfigParser()
    home = expanduser('~')
    aws_config.read(home + '/.aws/config')

    if not aws_config.has_section(CONFIG_PROFILE):
        print("Couldn't find configuration for profile: {}".format(PROFILE))
        sys.exit(1)

    config_section = aws_config[CONFIG_PROFILE]
    CLIENT_ID = config_section.get('oidc_client_id', None)
    AUTHORITY_URL = config_section.get('oidc_authority_url', None)
    ROLE_ARN = config_section.get('oidc_role_arn', None)

    if CLIENT_ID is None:
        _fail('client-id', PROFILE)
    if AUTHORITY_URL is None:
        _fail('authority-url', PROFILE)
    if ROLE_ARN is None:
        _fail('role-arn', PROFILE)


def _fail(missing_config, profile):
    print("No value for required configuration parameter {} in profile {}.".format(missing_config, profile))
    sys.exit(1)


def _parse_args():
    parser = argparse.ArgumentParser(description='AWS OIDC Login')
    parser.add_argument('profile', type=str, nargs='?', default='default',
                        help='AWS profile name to log in with')
    parser.add_argument('-w', '--web-console-login', action='store_true',
                        help='Open AWS Web Console in browser after login')
    parser.add_argument('-p', '--print-auth-url', action='store_true',
                        help='Print the authorize URL to stdout (so you can copy/paste it to browser manually')
    return parser.parse_args()


def _init_from_args(args):
    global PROFILE, CONFIG_PROFILE, WEB_CONSOLE_LOGIN, PRINT_AUTHORIZE_URL

    PROFILE = args.profile
    CONFIG_PROFILE = args.profile
    if CONFIG_PROFILE != 'default':
        CONFIG_PROFILE = 'profile {}'.format(PROFILE)

    PRINT_AUTHORIZE_URL = args.print_auth_url
    WEB_CONSOLE_LOGIN = args.web_console_login


if __name__ == "__main__":
    init()
