from setuptools import setup


with open('README.md', 'r') as fh:
    long_description = fh.read()


setup(
    name='pyzipei',
    version='0.1.0',
    author='PentairIoT',
    author_email='pentairiot@gmail.com',
    description='A utility library for retrieving electrical rates from OpenEI.org',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/pentairiot/PyZipEI',
    install_requires=["requests", "bs4"],
    packages=["pyzipei"],
    scripts=["PyZipEI"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
