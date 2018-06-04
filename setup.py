from setuptools import setup

setup(
    name = 'nise',
    version = '0.1.0',
    packages = ['nise'],
    entry_points = {
        'console_scripts': [
            'nise = nise.__main__:main'
        ]
    })
