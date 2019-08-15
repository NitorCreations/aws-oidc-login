# coding=utf8

from setuptools import setup

setup(name='aws-oidc-login',
      version='0.1.0',
      description='CLI login to AWS using OpenID Connect',
      url='http://github.com/NitorCreations/aws-oidc-login',
      download_url='https://github.com/NitorCreations/aws-oidc-login',
      author='Mika Majakorpi',
      author_email='mika.majakorpi@nitor.com',
      license='Apache 2.0',
      packages=[],
      include_package_data=True,
      scripts=[],
      entry_points={
          'console_scripts': ['aws-oidc-login=aws_oidc_login:aws_oidc_login'],
      },
      setup_requires=[],
      install_requires=[
          'boto3==1.9.208',
          'requests==2.22.0'],
      tests_require=[])
