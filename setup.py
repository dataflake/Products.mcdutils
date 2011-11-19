from setuptools import setup, find_packages

setup(
    name="mcdutils",
    version="0.2dev",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=["setuptools",
                      "Zope2"],
    )
