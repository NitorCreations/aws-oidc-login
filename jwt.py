from base64 import urlsafe_b64decode
import json


def get_email(jwt_str):
    payload = str(jwt_str.split(".")[1] + "===")  # https://gist.github.com/perrygeo/ee7c65bb1541ff6ac770
    decoded = urlsafe_b64decode(payload)
    print(decoded)
    jwt = json.loads(decoded)
    return jwt.get('email', 'no-email-in-oidc-token')
