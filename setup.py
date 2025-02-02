from setuptools import setup, find_packages

setup(
    name="blockchain-project",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'requests',
        'pytest',
        'pytest-cov',
        'cryptography',
    ],
) 