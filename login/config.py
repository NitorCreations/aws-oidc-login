
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


def init():
    global CLIENT_ID, AUTHORITY_URL, ROLE_ARN, PROFILE, CONFIG_PROFILE, WEB_CONSOLE_LOGIN
    args = parse_args()
    WEB_CONSOLE_LOGIN = args.web_console_login
    PROFILE = args.profile
    CONFIG_PROFILE = args.profile
    if CONFIG_PROFILE != 'default':
        CONFIG_PROFILE = 'profile {}'.format(PROFILE)

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
        fail('client-id', args.profile)
    if AUTHORITY_URL is None:
        fail('authority-url', args.profile)
    if ROLE_ARN is None:
        fail('role-arn', args.profile)


def fail(missing_config, profile):
    print("No value for required configuration parameter {} in profile {}.".format(missing_config, profile))
    sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description='AWS OIDC Login')
    parser.add_argument('profile', type=str, nargs='?', default='default',
                        help='AWS profile name to log in with')
    parser.add_argument('-w', '--web-console-login', action='store_true',
                        help='Open AWS Web Console in browser after login')

    return parser.parse_args()


if __name__ == "__main__":
    init()
