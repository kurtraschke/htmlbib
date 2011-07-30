from setuptools import setup, find_packages

setup(
    name="htmlbib",
    version="0.1",
    description="Generate interactive HTML from BibTeX",
    # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[],
    keywords="",
    author="Kurt Raschke",
    author_email='kurt@kurtraschke.com',
    url='http://github.com/kurtraschke/htmlbib',
    license='MIT',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Jinja2>=2.5.5',
        'appscript>=1.0.0'
    ],
    entry_points="""
    [console_scripts]
    htmlbib = htmlbib.makebib:main
    bibpreview = htmlbib.preview.engine:main
    """,
)
