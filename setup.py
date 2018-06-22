from setuptools import setup

setup(
    name = 'nise',
    version = '0.1.0',
    packages = [
        'nise',
        'nise.generators'
    ],
    install_requires=[
        'Faker',
        'boto3',
        'requests',
        'jinja2'
    ],
    entry_points = {
        'console_scripts': [
            'nise = nise.__main__:main'
        ]
    },
    include_package_data=True,
    zip_safe=False)
