from setuptools import setup

setup(
    name="koku-nise",
    version="1.0.3",
    author="Project Koku",
    author_email="cost_mgmt@redhat.com",
    description="A tool for generating sample cost and usage data for testing purposes.",
    url="https://github.com/project-koku/nise",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    packages=[
        "nise",
        "nise.generators",
        "nise.generators.aws",
        "nise.generators.ocp",
        "nise.generators.azure",
        "nise.generators.gcp",
    ],
    install_requires=[
        "faker>=3.0",
        "boto3>=1.11",
        "requests>=2.22",
        "jinja2>=2.10",
        "azure-mgmt-costmanagement>=0.1",
        "azure-mgmt-resource>=7.0",
        "azure-mgmt-storage>=7.1",
        "azure-storage-blob>=12.1",
        "google-cloud-storage>=1.19",
    ],
    dependency_links=[],
    entry_points={"console_scripts": ["nise = nise.__main__:main"]},
    include_package_data=True,
    zip_safe=False,
)
