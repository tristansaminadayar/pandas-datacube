from .pandasdatacube import *
from .SPARQL_query import *

__doc__ = """
Pandas Datacube - A python package to get datacube to dataframe 
using sparql
=====================================================================

**pandas-datacube** is a python package allowing to convert and  
download a datacube from a remote source using 
[SPARQL](https://www.w3.org/TR/sparql11-overview/) queries and to 
obtain a pandas dataframe

Main Features
-------------
  - automatically detects all datasets present in a SPARQL endpoint
  - detects all dimensions and measures of a dataset
  - download a dataset with the chosen characteristics
  - detects the metadata of a datacube
"""

