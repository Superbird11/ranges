import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python-ranges",
    version="0.1.2",
    author="Louis Jacobowitz",
    author_email="ldjacobowitzer@gmail.com",
    description="Continuous Range, RangeSet, and RangeDict data structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/superbird11/ranges",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    project_urls={
        'Documentation': 'https://python-ranges.readthedocs.io/en/latest/',
        'GitHub': 'https://github.com/Superbird11/ranges',
    },
    python_requires='>=3.6',
)