from setuptools import setup, find_packages

setup(
    name="higgs-to-invisible-python",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "coffea>=0.8",
        "uproot>=6.5",
        "awkward>=2.0",
        "numpy",
        "matplotlib"
    ],
    python_requires='>=3.10',
    description="Higgs to Invisible analysis framework using Coffea",
    author="Carsten Hensel",
    url="https://github.com/<your-username>/higgs-to-invisible-python",
)
