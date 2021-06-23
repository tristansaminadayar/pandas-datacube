import time as tm

import pandas as pd
from IPython.core.display import display
from ipywidgets import widgets

from SPARQL_query import SPARQLquery


def add_progress_bar(fun: callable):
    """
    Function that adds a loading bar to functions that download databases

    :param fun: The name of the function to modify
    :return: The modified function
    """
    def function_modif(*args, **kwargs):
        progress_bar = widgets.IntProgress(bar_style='success', description='Loading:')
        display(progress_bar)
        kwargs['widget'] = progress_bar
        ret = fun(*args, **kwargs)
        progress_bar.close()
        return ret

    return function_modif


@add_progress_bar
def get_datasets(endpoint: str, verbose: bool = False, widget: widgets.IntProgress = None) -> pd.DataFrame:
    """
    Get all datasets available names on a server and their description.

    :param endpoint: The address of the SPARQL server
    :param verbose: If the detail text will be displayed
    :param widget: If the detail widget will be displayed
    :return: The data frame of all datasets available names and their description
    """
    """SELECT ?song ?length {
    ?song a :Song .

}"""
    query: str = "SELECT DISTINCT ?dataset ?commentaire WHERE {?dataset a <http://purl.org/linked-data/cube#DataSet> \
    OPTIONAL {?dataset <http://www.w3.org/2000/01/rdf-schema#comment> ?commentaire}}"

    if verbose:
        print(tm.strftime(f"[%H:%M:%S] Requête au serveur des différents datasets disponible... "))

    list_datasets: pd.DataFrame = SPARQLquery(endpoint, query, verbose=verbose,
                                              widget=widget).do_query()  # We recovers all DataSets Structure

    if verbose:
        print(tm.strftime(f"[%H:%M:%S] Il y a {len(list_datasets)} datasets disponibles"))

    return list_datasets


@add_progress_bar
def get_features(endpoint: str, dataset_name: str, widget: widgets.IntProgress = None) -> pd.DataFrame:
    """
    Get all features available names on a dataset.

    :param endpoint: The address of the SPARQL server
    :param dataset_name: The name of the dataset where you want to have its features
    :param widget: If the detail widget will be displayed
    :return: The data frame of all datasets features names available
    """
    deb: str = "select ?property where { { select ?item where {?item <http://purl.org/linked-data/cube#dataSet> <"
    fin: str = "> } LIMIT 1 } ?item ?property ?value . filter \
    ( ?property not in (<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>) ) }"
    query: str = deb + dataset_name + fin

    result: pd.DataFrame = SPARQLquery(endpoint, query, widget=widget).do_query()
    return result


@add_progress_bar
def download_dataset(endpoint: str, dataset_name: str, features_names: list[str],
                     widget: widgets.IntProgress = None) -> pd.DataFrame:
    """
    Download and return all selected features of a dataset

    :param endpoint: The address of the SPARQL server
    :param dataset_name: The name of the dataset where you want to download its features
    :param features_names: The names of features to download
    :param widget: If the detail widget will be displayed
    :return: The data frame of selected and downloaded characteristics of a dataset
    """

    # We will build the query
    query: str = "SELECT "
    vars_list: list[str] = [item.split('#')[-1].split('/')[-1] for item in features_names]
    query += " ".join([f"?{item}" for item in vars_list])
    query += f" WHERE {'{'} ?o <http://purl.org/linked-data/cube#dataSet> <{dataset_name}> . "
    query += " ".join([f"?o <{uri}> ?{name} ." for uri, name in zip(features_names, vars_list)])
    query += " } "

    # Do the query
    return SPARQLquery(endpoint, query, widget=widget).do_query()
