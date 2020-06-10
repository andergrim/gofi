import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="gofi-andergrim",
    version="0.9.9",
    author="Kristoffer Andergrim",
    author_email="andergrim@gmail.com",
    description="GTK+3 Application launcher",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andergrim/gofi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Environment :: X11 Applications :: Gnome",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3.8',
)
