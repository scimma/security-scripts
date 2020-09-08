import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="security-scripts", # Replace with your own username
    version="0.9b",
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
        'console_scripts': ['sc=security_scripts.cli:catcher'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: none",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)