from setuptools import setup

setup(
    name="key-manager-app",
    version="0.1.0",
    py_modules=["main"],
    install_requires=[
        "PySide6>=6.8.0",
        "cryptography>=43.0.0",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
