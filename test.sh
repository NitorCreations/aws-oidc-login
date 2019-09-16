#!/bin/bash
set -e
PYENV_VERSION=p2-aws-saml2-login
pytest --cov=login --cov-report html
PYENV_VERSION=p35-aws-oidc-login
pytest --cov=login --cov-report html
PYENV_VERSION=p36-aws-oidc-login
pytest --cov=login --cov-report html
PYENV_VERSION=aws-saml2-login
pytest --cov=login --cov-report html
