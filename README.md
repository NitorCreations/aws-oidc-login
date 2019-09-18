# Log in to AWS using OpenID Connect

The aim for this is to create a general purpose CLI OIDC login with a limited set of trusted dependencies.

Tested with Azure AD. Your mileage may vary with other providers, please let us know!

[![Codeship Status for NitorCreations/aws-oidc-login](https://app.codeship.com/projects/c1b8cf70-ba79-0137-d140-5ec1c160b8c0/status?branch=master)](https://app.codeship.com/projects/364808)

## Setup (Azure AD example)
* Create Azure AD App
    * Set public client reply url to `http://localhost`
    * Add an appRole (may be unnecessary)
    * Add users(s) to the role (to the app)
* Create an AWS OIDC identity provider
    * Authority URL will be `https://login.microsoftonline.com/<AAD tenant id>/oauth2/v2.0`
    * Add your AAD app client id as audience
* Create a web identity role with permissions you'd like
    * Edit trust relationship for the role to allow role assumption with tokens issued by AAD for your app
* Add parameters under a suitable profile ~/.aws/config:
    * Add your application id (client id) from AAD app
    * Add your AAD tenant id
    * `oidc_authority_url=https://login.microsoftonline.com/<AAD tenant id>/oauth2/v2.0`
    * `oidc_client_id=<id of your AAD app>`
    * `oidc_role_arn=<ARN of the role you are assuming on AWS>`

## Install aws-oidc-login

Clone this repo and run `pip install aws-oidc-login` inside it.

## Run

The executable is called `aol`. Log in with default profile by simply running `aol` or specify a profile with `aol [profile]`. 

See `aol -h` for more options.
