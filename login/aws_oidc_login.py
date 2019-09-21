import json
# pypi dependencies
import boto3
import requests
from login import config
import login.jwt as jwt
from login.oidc_authorizer import OidcAuthenticationCodeFlowAuthorizer
from login import credentials
import webbrowser

try:
    # For Python 3.5 and later
    from urllib.parse import urlencode
    from urllib.parse import parse_qs
    from urllib.parse import unquote
    from urllib.parse import urlparse
    from urllib.parse import quote_plus
except ImportError:
    # Fall back to Python 2
    from urllib import urlencode   # noqa: F401
    from urlparse import parse_qs  # noqa: F401
    from urlparse import unquote   # noqa: F401
    from urlparse import urlparse  # noqa: F401
    from urllib import quote_plus


def get_aws_sts():
    return boto3.client('sts')


def web_console_login(assumed_role_object, session_duration=3600):
    # This code mostly from
    # https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles_providers_enable-console-custom-url.html

    url_credentials = {}
    url_credentials['sessionId'] = assumed_role_object.get('Credentials').get('AccessKeyId')
    url_credentials['sessionKey'] = assumed_role_object.get('Credentials').get('SecretAccessKey')
    url_credentials['sessionToken'] = assumed_role_object.get('Credentials').get('SessionToken')
    json_string_with_temp_credentials = json.dumps(url_credentials)

    # Make request to AWS federation endpoint to get sign-in token.
    request_parameters = "?Action=getSigninToken"
    request_parameters += "&SessionDuration={duration}".format(duration=session_duration)
    request_parameters += "&Session=" + quote_plus(json_string_with_temp_credentials)
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters
    r = requests.get(request_url)
    signin_token = json.loads(r.text)

    # Create URL where users can use the sign-in token to sign in to the console.
    request_parameters = "?Action=login"
    request_parameters += "&Issuer=aws-oidc-login"
    request_parameters += "&Destination=" + quote_plus("https://console.aws.amazon.com/")
    request_parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + request_parameters

    return request_url


def aws_oidc_login():
    config.init()
    oidc = OidcAuthenticationCodeFlowAuthorizer()
    token = oidc.get_id_token()
    email = jwt.get_email(token)

    print("Assuming role {}".format(config.ROLE_ARN))
    creds = aws_sts.assume_role_with_web_identity(
        RoleArn=config.ROLE_ARN,
        RoleSessionName=email,
        WebIdentityToken=token,
        DurationSeconds=3600
    )
    credentials.write(creds)
    if config.WEB_CONSOLE_LOGIN:
        login_url = web_console_login(creds, session_duration=3600)
        webbrowser.open_new_tab(login_url)
        print("console login url: {url}".format(url=login_url))


aws_sts = get_aws_sts()

if __name__ == "__main__":
    aws_oidc_login()
