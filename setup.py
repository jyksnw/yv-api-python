import os

from setuptools import setup


def read(file_name):
    return open(os.path.join(os.path.dirname(__file__), file_name), encoding='utf-8').read()

setup(
    name="youversion",
    version="0.0.2",
    author="Jason Snow",
    author_email="jsn.snw@gmail.com",
    description="YouVersion API Client",
    license="Apache License, Version 2.0",
    keywords="YouVersion Bible API Client",
    url="https://github.com/jyksnw/yv-api-python",
    packages=['youversion', 'tests'],
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    install_requires=['requests'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Religion",
        "Programming Language :: Python :: 3.7",
        "Topic :: Religion",
        "Topic :: Software Development",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
    ],
)
