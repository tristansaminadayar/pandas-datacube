import unittest

from pandasdatacube.pandasdatacube import *


class Tests(unittest.TestCase):
    def test_expand_name(self):
        expand_dict: dict = {'dbnary': 'http://kaiko.getalp.org/dbnary#',
                             'dbnstats': 'http://kaiko.getalp.org/dbnary/statistics/',
                             'lime': 'http://www.w3.org/ns/lemon/lime#'}
        self.assertEqual(expand_name('dbnstats:dbnaryNymRelationsCube', expand_dict),
                         'http://kaiko.getalp.org/dbnary/statistics/dbnaryNymRelationsCube')

        self.assertEqual(expand_name('dbnary:wiktionaryDumpVersion', expand_dict),
                         'http://kaiko.getalp.org/dbnary#wiktionaryDumpVersion')

        self.assertEqual(expand_name('wiktionaryDumpVersion', expand_dict),
                         'wiktionaryDumpVersion')

        self.assertEqual(expand_name('lime:language', expand_dict),
                         'http://www.w3.org/ns/lemon/lime#language')

        self.assertRaises(KeyError, expand_name, 'owl:language', expand_dict)

        self.assertRaises(ValueError, expand_name, 'owl:lime:language', expand_dict)

    def test_get_dataset(self):

        result = ['http://kaiko.getalp.org/dbnary/statistics/dbnaryNymRelationsCube',
                  'http://kaiko.getalp.org/dbnary/statistics/dbnaryStatisticsCube',
                  'http://kaiko.getalp.org/dbnary/statistics/dbnaryTranslationsCube',
                  'http://kaiko.getalp.org/dbnary/statistics/enhancementConfidenceDataCube',
                  'http://kaiko.getalp.org/dbnary/statistics/translationGlossesCube']

        endpoint = "http://kaiko.getalp.org/sparql"

        query_result = get_datasets(endpoint=endpoint, verbose=True).dataset.values

        for item in result:
            self.assertTrue(item in query_result)

    def test_get_feature(self):

        result = ['http://kaiko.getalp.org/dbnary#observationLanguage',
                  'http://kaiko.getalp.org/dbnary#wiktionaryDumpVersion',
                  'http://kaiko.getalp.org/dbnary#nymRelation',
                  'http://kaiko.getalp.org/dbnary#count']

        endpoint = "http://kaiko.getalp.org/sparql"

        dataset_name = 'http://kaiko.getalp.org/dbnary/statistics/dbnaryNymRelationsCube'

        query_result = get_features(endpoint=endpoint, dataset_name=dataset_name, verbose=True).property.values

        for item in result:
            self.assertTrue(item in query_result)

    def test_transform_features(self):

        result = (['http://purl.org/linked-data/sdmx/2009/dimension#refArea',
                   'http://purl.org/linked-data/sdmx/2009/dimension#refPeriod',
                   'http://purl.org/linked-data/cube#measureType',
                   'http://statistics.gov.scot/def/dimension/gender',
                   'http://statistics.gov.scot/def/dimension/workingPattern',
                   'http://statistics.gov.scot/def/dimension/populationGroup'],
                  ['http://statistics.gov.scot/def/measure-properties/median',
                   'http://statistics.gov.scot/def/measure-properties/mean'])

        query_result = get_features("https://statistics.gov.scot/sparql",
                                    'http://statistics.gov.scot/data/earnings')

        query_result = transform_features(query_result)

        self.assertTupleEqual(result, query_result)

    def test_transform_features2(self):

        result = (['http://kaiko.getalp.org/dbnary#observationLanguage',
                   'http://kaiko.getalp.org/dbnary#wiktionaryDumpVersion'],
                  ['http://kaiko.getalp.org/dbnary#lexicalEntryCount',
                   'http://kaiko.getalp.org/dbnary#lexicalSenseCount',
                   'http://kaiko.getalp.org/dbnary#pageCount',
                   'http://kaiko.getalp.org/dbnary#translationsCount'])

        query_result = get_features("http://kaiko.getalp.org/sparql",
                                    'http://kaiko.getalp.org/dbnary/statistics/dbnaryStatisticsCube')

        query_result = transform_features(query_result)

        self.assertTupleEqual(result, query_result)

    def test_download_dataset(self):

        query_result = get_features("http://kaiko.getalp.org/sparql",
                                    'http://kaiko.getalp.org/dbnary/statistics/dbnaryStatisticsCube')

        query_result = transform_features(query_result)

        query_result = download_dataset("http://kaiko.getalp.org/sparql",
                                        'http://kaiko.getalp.org/dbnary/statistics/dbnaryStatisticsCube',
                                        query_result[0],
                                        query_result[1],
                                        {'http://kaiko.getalp.org/dbnary#wiktionaryDumpVersion': ['20210701']})

        self.assertEqual(len(query_result), 21)
        self.assertEqual(len(query_result.columns), 4)
        self.assertEqual(len(query_result.reset_index()['wiktionaryDumpVersion'].unique()), 1)

    def test_download_dataset2(self):

        query_result = get_features("http://kaiko.getalp.org/sparql",
                                    'http://kaiko.getalp.org/dbnary/statistics/dbnaryStatisticsCube')

        query_result = transform_features(query_result)

        self.assertRaises(KeyError, download_dataset, "http://kaiko.getalp.org/sparql",
                          'http://kaiko.getalp.org/dbnary/statistics/dbnaryStatisticsCube',
                          query_result[0],
                          query_result[1],
                          {'wiktionaryDumpVersion': ['20210701']})

    def test_get_datacube(self):

        endpoint: str = "http://kaiko.getalp.org/sparql"
        prefixes: dict[str] = {'dbnary': 'http://kaiko.getalp.org/dbnary#',
                               'dbnstats': 'http://kaiko.getalp.org/dbnary/statistics/',
                               'lime': 'http://www.w3.org/ns/lemon/lime#'}

        dataset: str = "dbnstats:dbnaryNymRelationsCube"
        dimensions: list[str] = ['dbnary:wiktionaryDumpVersion', 'dbnary:nymRelation', 'dbnary:observationLanguage']
        mesures: list[str] = ['dbnary:count']
        dtypes: dict[str] = {'count': int}

        query_result = get_datacube(endpoint, dataset, dimensions, mesures, dtypes, prefixes).reset_index()

        self.assertGreaterEqual(len(query_result), 27003)

    def test_get_datacube2(self):

        endpoint: str = "http://kaiko.getalp.org/sparql"

        query_result = get_datacube(endpoint).reset_index()

        self.assertGreaterEqual(len(query_result), 27003)

    def test_get_datacube3(self):

        self.assertRaises(KeyError, get_datacube, "https://dbpedia.org/sparql/")

    def test_sparql_query(self):

        query = "DESCRIBE ?item WHERE {?item a qb:Observation . ?item qb:dataSet dbnstats:dbnaryNymRelationsCube}"
        self.assertWarns(RuntimeWarning, SPARQLquery("http://kaiko.getalp.org/sparql", query).do_query)


if __name__ == '__main__':
    unittest.main()
