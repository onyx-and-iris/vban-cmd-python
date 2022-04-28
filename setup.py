from setuptools import setup

setup(
    name="vbancmd",
    version="0.0.1",
    description="VBAN CMD Python API",
    packages=["vbancmd"],
    install_requires=["toml"],
    extras_require={"development": ["pytest", "pytest-randomly", "genbadge[tests]"]},
)
