# Log in to AWS using Azure AD OpenID Connect

The aim for this is to keep away from promiscuous dependencies often seen in AWS login tools like `aws-azure-login` and `aws-cli-oidc`.

## Setup
* Create Azure AD App
    * Set public client reply url to `http://localhost`
    * Add an appRole (may be unnecessary)
    * Add users(s) to the role (to the app)
* Modify `config.py`
    * Add your application id (client id) from AAD app
    * Add your AAD tenant id
* Create an AWS OIDC identity provider
    * Use your authority URL from `config.py` (with templating applied)
    * Add your client id as audience
* Create a web identity role with permissions you'd like
    * Edit trust relationship for the role to allow role assumption with tokens issued by AAD for your app

## Run

`python aws-oidc-login.py <role-arn-here>`

## To Do

* Get past prototype stage by cleaning things up
    * Add command line option for console login url and maybe opening browser there
* Use parameters from ~/.aws/config and write credentials to ~/.aws/credentials
    * Support profiles
