import re
import time as tm
from typing import Any

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


@add_progress_bar
def get_datasets(endpoint: str, verbose: bool = False, widget: widgets.IntProgress = None) -> pd.DataFrame:
    """
    Get all datasets available names on a server and their description.

    :param endpoint: The address of the SPARQL server
    :param verbose: If the detail text will be displayed
    :param widget: If the detail widget will be displayed
    :return: The data frame of all datasets available names and their description
    """

    query: str = ("SELECT DISTINCT ?structure ?dataset ?commentaire WHERE "
                  "{?dataset a <http://purl.org/linked-data/cube#DataSet> . "
                  "?dataset <http://purl.org/linked-data/cube#structure> ?structure "
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
def get_features(endpoint: str, dataset_structure: str, widget: widgets.IntProgress = None,
                 verbose: bool = False) -> pd.DataFrame:
    """
    Get all features available names on a dataset.

    :param verbose: If the detail text will be displayed
    :param endpoint: The address of the SPARQL server
    :param dataset_structure: The URI of the structure of the dataset where you want to have its features
    :param widget: If the detail widget will be displayed
    :return: The data frame of all datasets features names available
    """

    query: str = f"""select distinct ?type ?property where {{
        {{ select ?item where {{ <{dataset_structure}> <http://purl.org/linked-data/cube#component> ?item }} }}
        ?item ?type ?property }}"""

    result: pd.DataFrame = SPARQLquery(endpoint, query, widget=widget, verbose=verbose).do_query()

    return result[result['type'].isin(["http://purl.org/linked-data/cube#dimension", "http://purl.org/linked-data/cube#measure"])]


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
