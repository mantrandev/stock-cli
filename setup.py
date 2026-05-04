from setuptools import find_packages, setup


setup(
    name="stockcli",
    version="0.2.0",
    description="Terminal CLI for Vietnam stock quotes and a local JSON portfolio.",
    python_requires=">=3.9",
    packages=find_packages(),
    entry_points={"console_scripts": ["stock=stockcli.cli:main", "crypto=stockcli.cli:crypto_main"]},
)
