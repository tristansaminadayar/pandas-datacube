import time as tm
from typing import NoReturn

import pandas as pd
from SPARQLWrapper import SPARQLWrapper
from ipywidgets import widgets


class SPARQLquery:
    """
    Class allowing to make a query on a remote SPARQL server, its main characteristics are :
     - Taking into account the big answers by concatenating them as they are received
     - Ability to access the size of the database
     - Ability to retrieve the response in `pandas` data frame format
    """

    def __init__(self, endpoint: str, query: str, verbose: bool = False, step: int = 1000,
                 widget: widgets.IntProgress = None) -> NoReturn:
        """


        :param endpoint: Url to the remote SPARQL service
        :param query: The query
        :param verbose: If the detail text will be displayed
        :param step: The max number of result to receive
        """
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat("json")

        self.query: str = query
        self.verbose: bool = verbose
        self.step: int = step
        self.resultSize: int = self.get_result_size()
        self.is_widget: bool = False

        if widget:
            self.widget = widget
            self.widget.max = self.resultSize
            self.widget.value = 0
            self.is_widget = True

    def get_result_size(self) -> int:
        """
        Function return the size of a query (only in SELECT query).
        """

        if self.query.strip().startswith("SELECT") or self.query.strip().startswith(
                "select"):  # Modifie the query to count the number of answer

            if self.verbose:
                print(tm.strftime(f"[%H:%M:%S] Obtention du nombre de résultats avant exécuter la requête"))

            start: int = 7  # We detect the position of the first variable after the select
            while self.query[start] != '?':
                start += 1
            end: int = start
            while self.query[end:end + 5] != "WHERE" and self.query[end:end + 5] != "where":
                end += 1

            mot: str = self.query[start: end - 1]  # THe name of the variable

            self.sparql.setQuery(self.query.replace(mot, f"(COUNT (*) as ?cnt)", 1))
            processed_results: dict = self.sparql.query().convert()  # Do the query
            number_of_results: int = int(processed_results['results']['bindings'][0]['cnt']['value'])

            if self.verbose:
                print(tm.strftime(f"[%H:%M:%S] Il y a  {number_of_results} résultats..."))

            return number_of_results
        return 1

    def get_sparql_dataframe(self, query: str, text: str = "") -> pd.DataFrame:
        """
        Helper function to convert SPARQL results into a Pandas data frame.

        Credit: Douglas Fils

        :param query: The query to perform
        :param text: optional text to print in verbose mode
        """

        if self.verbose:
            print(tm.strftime(f"[%H:%M:%S] Transmission {text} en cours..."), end='')

        self.sparql.setQuery(query)

        processed_results: dict = self.sparql.query().convert()

        if self.verbose:
            print(tm.strftime(f"\r[%H:%M:%S] Transmission {text} réussi, conversion en Data Frame..."), end='')

        cols = processed_results['head']['vars']

        out = [[row.get(c, {}).get('value') for c in cols] for row in processed_results['results']['bindings']]

        if self.is_widget:
            if text == "":
                self.widget.value = self.widget.max
            else:
                self.widget.value = int(text.split(' ')[0])

        if self.verbose:
            print(tm.strftime(f" Effectué"))

        return pd.DataFrame(out, columns=cols)

    def do_query(self) -> pd.DataFrame:
        """
        Performs the query all at once if the result is not too big or little by little otherwise,
        if the query is not a selection it will be done all at once.

        :return: The result of the query
        """
        if self.resultSize > self.step:
            query = self.query + f" LIMIT {self.step}"
            return pd.concat(
                [self.get_sparql_dataframe(query + f" OFFSET {value}", f"{value} sur {self.resultSize}") for value in
                 range(0, self.resultSize, self.step)])
        return self.get_sparql_dataframe(self.query)


def get_datasets(endpoint: str, verbose: bool = False, widget: widgets.IntProgress = None):
    """
    Dbnary specific function;

    Get all datasets available names on Dbnary and their description.

    :param endpoint: The address of the SPARQL server
    :param verbose: If the detail text will be displayed
    :param widget: If the detail widget will be displayed
    :return: The data frame of all datasets available names and their description
    """

    query: str = "SELECT ?dataset ?commentaire WHERE {?dataset a qb:DataSet ; rdfs:comment ?commentaire}"

    if verbose:
        print(tm.strftime(f"[%H:%M:%S] Requête au serveur des différents datasets disponible... "))

    list_datasets: pd.DataFrame = SPARQLquery(endpoint, query, verbose=verbose,
                                              widget=widget).do_query()  # We recovers all DataSets Structure

    if verbose:
        print(tm.strftime(f"[%H:%M:%S] Il y a {len(list_datasets)} datasets disponibles"))

    return list_datasets


def get_features(endpoint: str, dataset_name: str, widget: widgets.IntProgress = None) -> pd.DataFrame:
    """
    Dbnary specific function;

    Get all features available names on a dataset in Dbnary.

    :param endpoint: The address of the SPARQL server
    :param dataset_name: The name of the dataset where you want to have its features
    :param widget: If the detail widget will be displayed
    :return: The data frame of all datasets features names available
    """
    query: str = f"""DESCRIBE ?item WHERE {'{'} ?item qb:dataSet <{dataset_name}> {'}'} LIMIT 1"""
    result: pd.DataFrame = SPARQLquery(endpoint, query, widget=widget).do_query()
    return result['p'].to_frame(name=None).set_axis(["Caractéristiques"], axis=1)


def download_dataset(endpoint: str, dataset_name: str, features_names: list[str],
                     widget: widgets.IntProgress = None) -> pd.DataFrame:
    """
    Dbnary specific function;

    Download and return all selected features of a dataset

    :param endpoint: The address of the SPARQL server
    :param dataset_name: The name of the dataset where you want to download its features
    :param features_names: The names of features to download
    :param widget: If the detail widget will be displayed
    :return: The data frame of selected and downloaded characteristics of a dataset
    """

    # We will build the query
    query: str = "SELECT "
    vars_list: list[str] = [item.split('#')[-1] for item in features_names]
    for item in vars_list:
        query += f"?{item} "
    query += f"WHERE {'{'} ?o qb:dataSet <{dataset_name}> . "
    for uri, name in zip(features_names, vars_list):
        query += f"?o <{uri}> ?{name} . "
    query += "} "

    # Do the query
    return SPARQLquery(endpoint, query, widget=widget).do_query()
