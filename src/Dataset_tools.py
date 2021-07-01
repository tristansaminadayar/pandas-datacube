import re
import time as tm
from typing import Any, Union

import pandas as pd
from IPython.core.display import display
from ipywidgets import widgets

from SPARQL_query import SPARQLquery


def add_progress_bar(fun: callable) -> callable:
    """
    Function that adds a loading bar to functions that download databases

    :param fun: The name of the function to modify
    :return: The modified function
    """

    def function_modif(*args, **kwargs) -> Any:
        progress_bar: widgets.IntProgress = widgets.IntProgress(bar_style='success', description='Loading:')
        display(progress_bar)
        kwargs['widget'] = progress_bar
        ret: Any = fun(*args, **kwargs)
        progress_bar.close()
        return ret

    return function_modif


def expand_name(word: str, prefixes: dict[str]) -> str:
    """
    Function that transforms the prefix using a dictionary of conversions

    Exemple:

    expand_name("dbo:PopulatedPlace/areaTotal", {'dbo': 'https://dbpedia.org/ontology/'})
    > "https://dbpedia.org/ontology/PopulatedPlace/areaTotal"


    :param word: The word to expand
    :param prefixes: The dictionary of conversions
    :return: the word expanded
    """
    name = word.split(':')

    if len(name) == 1:
        return name[0]
    elif len(name) == 2:
        expanded: str = ""
        for key in prefixes:
            if key == name[0]:
                expanded = prefixes[key]
        if expanded == "":
            raise KeyError(f"{name[0]} does not belong to the known prefixes and cannot be expanded")
        return expanded + name[1]
    else:
        raise ValueError(f"There are several ':' in the word expanded {word}")


@add_progress_bar
def get_datasets(endpoint: str, verbose: bool = False, widget: widgets.IntProgress = None) -> pd.DataFrame:
    """
    Get all datasets available names on a server and their description.

    :param endpoint: The address of the SPARQL server
    :param verbose: If the detail text will be displayed
    :param widget: If the detail widget will be displayed
    :return: The data frame of all datasets available names and their description
    """

    query: str = ("SELECT DISTINCT ?dataset ?commentaire WHERE "
                  "{?dataset a <http://purl.org/linked-data/cube#DataSet> "
                  "OPTIONAL {?dataset <http://www.w3.org/2000/01/rdf-schema#comment> ?commentaire }}"
                  )

    if verbose:
        print(tm.strftime(f"[%H:%M:%S] Requête au serveur des différents datasets disponible... "))

    list_datasets: pd.DataFrame = SPARQLquery(endpoint, query, verbose=verbose,
                                              widget=widget).do_query()  # We recovers all DataSets Structure

    if verbose:
        print(tm.strftime(f"[%H:%M:%S] Il y a {len(list_datasets)} datasets disponibles"))

    return list_datasets


@add_progress_bar
def get_features(endpoint: str, dataset_name: str, widget: widgets.IntProgress = None,
                 verbose: bool = False) -> pd.DataFrame:
    """
    Get all features available names on a dataset.

    :param verbose: If the detail text will be displayed
    :param endpoint: The address of the SPARQL server
    :param dataset_name: The URI of the dataset where you want to have its features
    :param widget: If the detail widget will be displayed
    :return: The data frame of all datasets features names available
    """

    query: str = ("select distinct ?item ?type ?property where {\n{select ?item where { "
                  f"<{dataset_name}> <http://purl.org/linked-data/cube#structure> ?structure . ?structure"
                  " <http://purl.org/linked-data/cube#component> ?item}}\n ?item ?type ?property }")

    return SPARQLquery(endpoint, query, widget=widget, verbose=verbose).do_query()


def transform_features(features: pd.DataFrame) -> tuple[list[str], list[str]]:
    """
    Transform the dataframe obtained by `get_features` to a list of all measures and dimensions,
    if the order component is in the cube, the dimensions list will be sorted

    :param features: The dataframe obtained by `get_features`
    :return: The list of all dimensions and the list of all measures
    """

    unique_features: list[str] = features['item'].unique()  # Get all unique measure/dimension of the dataset

    order: bool = False  # Check if the attribut order is filled
    if "http://purl.org/linked-data/cube#order" in features['type']:
        order = True

    dimensions: list[Union[str, tuple[str, int]]] = []
    measures: list[str] = []

    for feature in unique_features:
        data: pd.DataFrame = features[features['item'] == feature]
        compo: pd.DataFrame = data[data['type'].isin(
            ['http://purl.org/linked-data/cube#dimension',
             'http://purl.org/linked-data/cube#measure',
             'http://purl.org/linked-data/cube#attribute'])]

        if compo['type'].values[0] == 'http://purl.org/linked-data/cube#measure':
            measures.append(compo['property'].values[0])
        elif compo['type'].values[0] == 'http://purl.org/linked-data/cube#dimension':
            if order:
                value = int(data[data['type'] == 'http://purl.org/linked-data/cube#order']['property'].values[0])
                dimensions.append((compo['property'].values[0], value))
            else:
                dimensions.append(compo['property'].values[0])

    if order:
        dimensions.sort(key=lambda x: x[1])
        dimensions: list[str] = list(map(lambda x: x[0], dimensions, ))

    return dimensions, measures


@add_progress_bar
def download_dataset(endpoint: str, dataset_name: str, dimensions: list[str], measures: list[str],
                     widget: widgets.IntProgress = None, verbose: bool = False) -> pd.DataFrame:
    """
    Download and return all selected features of a dataset

    :param verbose: If the detail text will be displayed
    :param endpoint: The address of the SPARQL server
    :param dataset_name: The name of the dataset where you want to download its features
    :param measures: The names of mesures to download
    :param dimensions: The names of dimensions to download
    :param widget: If the detail widget will be displayed
    :return: The data frame of selected and downloaded characteristics of a dataset
    """

    # We will build the query
    query: str = "SELECT "
    measures_name: list[str] = [re.sub('[^A-Za-z0-9]+', '', item.split('#')[-1].split('/')[-1]) for item in measures]
    dimensions_name: list[str] = [re.sub('[^A-Za-z0-9]+', '', item.split('#')[-1].split('/')[-1]) for item in
                                  dimensions]
    vars_list: list[str] = dimensions_name + measures_name
    url_list: list[str] = dimensions + measures

    query += " ".join([f"?{item}" for item in vars_list])
    query += f" WHERE {'{'} ?o <http://purl.org/linked-data/cube#dataSet> <{dataset_name}> . "
    query += " ".join([f"OPTIONAL{{ ?o <{uri}> ?{name} }}" for uri, name in zip(url_list, vars_list)])
    query += " } "

    # Do the query
    return SPARQLquery(endpoint, query, widget=widget, verbose=verbose).do_query().set_index(dimensions_name)


def from_datacube(sparql_endpoint: str, dataset_name: str = "", dimensions: list[str] = None,
                  measures: list[str] = None, dtypes: dict[type] = None, prefixes: dict[str] = None) -> pd.DataFrame:
    """
    Function to download a datacube


    :param prefixes: The dictionary of the namespace prefixes
    :param sparql_endpoint: The URL of the SPARQL endpoint
    :param dataset_name: The name of the datacube (default: a random datacube)
    :param dimensions: The dimensions of the datacube to download (default: all dimensions)
    :param measures: The measures of the datacube to download (default: all measures)
    :param dtypes: The type of measures (default: str)
    :return: A dataframe containing the result, with measures indexed by dimensions
    """

    # The case where prefixes has been given
    if prefixes is not None:
        dataset_name = expand_name(dataset_name, prefixes)
        measures = [expand_name(measure, prefixes) for measure in measures]
        dimensions = [expand_name(dimension, prefixes) for dimension in dimensions]

    # The case where no dataset_name has been given
    if dataset_name == "":
        list_datasets: pd.DataFrame = get_datasets(sparql_endpoint)
        if len(list_datasets) == 0:
            raise KeyError(f"No datasets was found in this endpoint ({sparql_endpoint})")
        else:
            dataset_name = list_datasets['dataset'].values[0]

    # The case where no dimension or/and measures has been given
    if len(measures) == 0 or len(dimensions) == 0:
        full_dim, full_msr = transform_features(get_features(sparql_endpoint, dataset_name))
        if len(dimensions) == 0:
            dimension = full_dim
        if len(measures) == 0:
            measures = full_dim

    dataframe: pd.DataFrame = download_dataset(sparql_endpoint, dataset_name, dimensions, measures)

    # The case where types has been given
    for key in dtypes:
        dataframe[key] = dataframe[key].astype(dtypes[key])

    return dataframe
