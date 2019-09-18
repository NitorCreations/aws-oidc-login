# coding=utf8

import pathlib2
from setuptools import setup

HERE = pathlib2.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(name='aws-oidc-login',
      version='0.1.1',
      description='CLI login to AWS using OpenID Connect',
      long_description=README,
      long_description_content_type="text/markdown",
      url='http://github.com/NitorCreations/aws-oidc-login',
      download_url='https://github.com/NitorCreations/aws-oidc-login',
      author='Mika Majakorpi',
      author_email='mika.majakorpi@nitor.com',
      license='Apache 2.0',
      packages=['login'],
      include_package_data=True,
      scripts=[],
      entry_points={
          'console_scripts': ['aol=login.aws_oidc_login:aws_oidc_login'],
      },
      setup_requires=['pytest-runner', 'wheel', 'pathlib2'],
      install_requires=[
          'boto3==1.9.208',
          'requests==2.22.0',
          'argparse==1.4.0'],
      tests_require=[
          'pytest==4.6.5',
          'pytest-mock==1.10.4',
          'pytest-cov==2.7.1',
          'requests-mock==1.6.0',
          'pytest-runner'
      ],
      test_suite='tests')
