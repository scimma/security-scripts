import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scimma-security-scripts", # Replace with your own username
    version="1.1b",
    author="Vladislav Ekimtcov, Donald Petravic",
    author_email="ekimtco2@illinois.edu",
    description="SCiMMA security scripts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scimma/security-scripts",
    packages=setuptools.find_packages(),
    package_data={
        "": ["*.cfg"] # carry what is yours
    },
    install_requires=['boto3','tabulate'],
    entry_points={
        'console_scripts': ['sc=security_scripts.kli:catcher'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License", # https://pypi.org/pypi?%3Aaction=list_classifiers
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)