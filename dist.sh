#!/bin/bash
rm -rf build dist
python setup.py sdist bdist_wheel
VERSION=$1
keybase pgp sign -d -i dist/aws_oidc_login-${VERSION}-py2.py3-none-any.whl -o dist/aws_oidc_login-${VERSION}-py2.py3-none-any.whl.asc
keybase pgp sign -d -i dist/aws-oidc-login-${VERSION}.tar.gz -o dist/aws-oidc-login-${VERSION}.tar.gz.asc
