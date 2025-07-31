from setuptools import setup, find_packages

setup(
    name="qpymenu",
    version="0.8.0",
    description="A quick and simple terminal menu system with ANSI formatting and logging.",
    author="David J. Cartwright",
    author_email="davidcartwright@hotmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    include_package_data=True,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)