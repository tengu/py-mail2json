import os
from setuptools import setup

setup(
    name = "mail2json",
    version = "0.1",
    url = "https://github.com/tengu/py-mail2json",
    description = "convert email to json",
    packages = ['mail2json'],
    entry_points={"console_scripts": [ 'mail2json=mail2json:main' ]},
    install_requires=['baker'],
    zip_safe=False,
)
