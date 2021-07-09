from setuptools import setup, find_packages

requirements = ['pandas', 'sparqlwrapper']

setup(
    name='pandas-datacube',
    version='0.0.2',
    packages=find_packages(),
    url='https://github.com/tristansaminadayar/pandas-datacube',
    license='MIT',
    author='Tristan Saminadayar',
    author_email='tristan.saminadayar@gmail.com',
    description='A package allowing to download datacubes into pandas data frames',
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English',
        'Topic :: Database'],
    zip_safe=False
)
