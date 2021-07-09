pandas-datacube
======

## About

**pandas-datacube** is a python package allowing to convert and download a datacube from a remote source using
SPARQL](https://www.w3.org/TR/sparql11-overview/) queries and to obtain a pandas dataframe

## Installation

You can install pandas-datacube from PyPi:

```
$ pip install pandas-datacube
```

## How to use

The module is quite simple to use:

- get all datasets available:
   ```python
   from pandasdatacube import get_datasets
   import pandas as pd 
  
   ENDPOINT: str = "https://statistics.gov.scot/sparql"
   
   datasets: pd.DataFrame = get_datasets(ENDPOINT)
 
   datasets.head()
   ```
  |    | dataset                                                                   | commentaire |
    |---:|:--------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------|
  |  0 | http://statistics.gov.scot/data/pupil-attainment                          | Number of pupils who attained a given number of qualifications by level and stage.                                                           |
  |  1 | http://statistics.gov.scot/data/alcohol-related-discharge                 | Number and European Age-sex Standardised Rates (EASRs) of general acute inpatient and day case discharges with an alcohol-related diagnosis. |
  |  2 | http://statistics.gov.scot/data/business-births-deaths-and-survival-rates | Number and rate (per 10,000 adults) of VAT/PAYE registrations, de-registrations and business survival rates                                  |
  |  3 | http://statistics.gov.scot/data/earnings                                  | Mean and median gross weekly earnings (£s) by gender, working pattern and workplace/residence measure.                                       |
  |  4 | http://statistics.gov.scot/data/economic-inactivity                       | Economic inactivity level and rate by gender|

- get and transform features of a dataset
   ```python
   from pandasdatacube import get_features, transform_features
   import pandas as pd

   ENDPOINT: str = "https://statistics.gov.scot/sparql"
   DATASET_NAME: str = "http://statistics.gov.scot/data/earnings"

   features: pd.DataFrame = get_features(ENDPOINT, DATASET_NAME)
   
   features.head()
   ```
  |    | item                                                                      | type                                            | property |
    |---:|:--------------------------------------------------------------------------|:------------------------------------------------|:----------------------------------------------------------|
  |  0 | http://statistics.gov.scot/def/component-specification/earnings/refArea   | http://www.w3.org/1999/02/22-rdf-syntax-ns#type | http://purl.org/linked-data/cube#ComponentSpecification   |
  |  1 | http://statistics.gov.scot/def/component-specification/earnings/refArea   | http://purl.org/linked-data/cube#dimension      | http://purl.org/linked-data/sdmx/2009/dimension#refArea   |
  |  2 | http://statistics.gov.scot/def/component-specification/earnings/refArea   | http://purl.org/linked-data/cube#order          | 1
  |
  |  3 | http://statistics.gov.scot/def/component-specification/earnings/refArea   | http://purl.org/linked-data/cube#codeList       | http://statistics.gov.scot/def/code-list/earnings/refArea |
  |  4 | http://statistics.gov.scot/def/component-specification/earnings/refPeriod | http://www.w3.org/1999/02/22-rdf-syntax-ns#type | http://purl.org/linked-data/cube#ComponentSpecification   |

   ```python
   transformed_features: tuple[list[str]] = transform_features(features)
   print(transformed_features)
  ```
  Output:
  ```python
  (['http://purl.org/linked-data/sdmx/2009/dimension#refArea',
   'http://purl.org/linked-data/sdmx/2009/dimension#refPeriod',
   'http://purl.org/linked-data/cube#measureType',
   'http://statistics.gov.scot/def/dimension/gender',
   'http://statistics.gov.scot/def/dimension/workingPattern', 
   'http://statistics.gov.scot/def/dimension/populationGroup'],
  ['http://statistics.gov.scot/def/measure-properties/median',
   'http://statistics.gov.scot/def/measure-properties/mean'])
  ```

 - download a dataset

   ```python
   from pandasdatacube import download_dataset
   import pandas as pd
   
   ENDPOINT: str = "https://statistics.gov.scot/sparql"
   DATASET_NAME: str = "http://statistics.gov.scot/data/earnings"
   DIMENSIONS: list[str] = ['http://purl.org/linked-data/sdmx/2009/dimension#refArea',
                            'http://purl.org/linked-data/sdmx/2009/dimension#refPeriod',
                            'http://purl.org/linked-data/cube#measureType',
                            'http://statistics.gov.scot/def/dimension/gender',
                            'http://statistics.gov.scot/def/dimension/workingPattern', 
                            'http://statistics.gov.scot/def/dimension/populationGroup']
   MEASURES: list[str] = ['http://statistics.gov.scot/def/measure-properties/median',
                          'http://statistics.gov.scot/def/measure-properties/mean']
                       
   
   data: pd.DataFrame = download_dataset(
        endpoint =ENDPOINT,
        dataset_name=DATASET_NAME,
        dimensions=DIMENSIONS,
        measures=MEASURES
   )
   
   data.head().reset_index()
   ```
  |    | refArea                                                       | refPeriod                                 | measureType | gender                                               | workingPattern                                                   | populationGroup |   median |   mean |
  |---:|:--------------------------------------------------------------|:------------------------------------------|:---------------------------------------------------------|:-----------------------------------------------------|:-----------------------------------------------------------------|:------------------------------------------------------------------------|---------:|-------:|
  |  0 | http://statistics.gov.scot/id/statistical-geography/S92000003 | http://reference.data.gov.uk/id/year/1997 | http://statistics.gov.scot/def/measure-properties/median | http://statistics.gov.scot/def/concept/gender/male   | http://statistics.gov.scot/def/concept/working-pattern/full-time | http://statistics.gov.scot/def/concept/population-group/workplace-based |    340.8 |        |
  |  1 | http://statistics.gov.scot/id/statistical-geography/S92000003 | http://reference.data.gov.uk/id/year/1997 | http://statistics.gov.scot/def/measure-properties/mean   | http://statistics.gov.scot/def/concept/gender/male   | http://statistics.gov.scot/def/concept/working-pattern/full-time | http://statistics.gov.scot/def/concept/population-group/workplace-based |          |  387.1 |
  |  2 | http://statistics.gov.scot/id/statistical-geography/S92000003 | http://reference.data.gov.uk/id/year/1997 | http://statistics.gov.scot/def/measure-properties/median | http://statistics.gov.scot/def/concept/gender/male   | http://statistics.gov.scot/def/concept/working-pattern/part-time | http://statistics.gov.scot/def/concept/population-group/workplace-based |     80   |        |
  |  3 | http://statistics.gov.scot/id/statistical-geography/S92000003 | http://reference.data.gov.uk/id/year/1997 | http://statistics.gov.scot/def/measure-properties/mean   | http://statistics.gov.scot/def/concept/gender/male   | http://statistics.gov.scot/def/concept/working-pattern/part-time | http://statistics.gov.scot/def/concept/population-group/workplace-based |          |  110.9 |
  |  4 | http://statistics.gov.scot/id/statistical-geography/S92000003 | http://reference.data.gov.uk/id/year/1997 | http://statistics.gov.scot/def/measure-properties/median | http://statistics.gov.scot/def/concept/gender/female | http://statistics.gov.scot/def/concept/working-pattern/full-time | http://statistics.gov.scot/def/concept/population-group/workplace-based |    247   |        |

 - do all steps in one lines

   ```python
   from pandasdatacube import get_datacube
   import pandas as pd
   
   ENDPOINT: str = "http://kaiko.getalp.org/sparql"
   PREFIXES: dict[str] = {'dbnary': 'http://kaiko.getalp.org/dbnary#',
                       'dbnstats': 'http://kaiko.getalp.org/dbnary/statistics/',
                       'lime': 'http://www.w3.org/ns/lemon/lime#'}
   
   dataset: str = "dbnstats:dbnaryStatisticsCube"
   dimensions: list[str] = ['dbnary:observationLanguage', 'dbnary:wiktionaryDumpVersion']
   mesures: list[str] = ['dbnary:lexicalEntryCount', 'dbnary:lexicalSenseCount', 'dbnary:pageCount', 'dbnary:translationsCount']
   dtypes: dict[str] = {"lexicalEntryCount": int, "translationsCount": int, "lexicalSenseCount": int, "pageCount": int}
    
   data: pd.DataFrame = get_datacube(ENDPOINT, dataset, dimensions, mesures, dtypes, PREFIXES)

   data.head().reset_index()
   ```
   |    | observationLanguage   |   wiktionaryDumpVersion |   lexicalEntryCount |   lexicalSenseCount |   pageCount |   translationsCount |
   |---:|:----------------------|------------------------:|--------------------:|--------------------:|------------:|--------------------:|
   |  0 | bg                    |                20210701 |               18626 |               18420 |       27050 |               18086 |
   |  1 | bg                    |                20140224 |               18831 |               18798 |       27071 |               13888 |
   |  2 | bg                    |                20140312 |               18829 |               18796 |       27068 |               13895 |
   |  3 | bg                    |                20140328 |               18828 |               18795 |       27072 |               13909 |
   |  4 | bg                    |                20140415 |               18822 |               18294 |       27068 |               13920 |

