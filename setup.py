import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fin_app_core",
    version="0.0.1",
    author="Gabriel Helie",
    author_email="ghfin123@gmail.com",
    description="Semi and fully automated trading with python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clockworcarry/fin_app_core",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux",
    ],
    python_requires='>=3.6',
)