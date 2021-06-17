import time as tm
import pandas as pd
from SPARQLWrapper import SPARQLWrapper
from typing import NoReturn


class SPARQLquery:
    """
    Class allowing to make a query on a remote SPARQL server, its main characteristics are :
     - Taking into account the big answers by concatenating them as they are received
     - Ability to access the size of the database
     - Ability to retrieve the response in `pandas` data frame format
    """

    def __init__(self, endpoint: str, query: str, verbose: bool = False, step: int = 5000) -> NoReturn:
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

    def get_result_size(self) -> int:
        """
        Function return the size of a query (only in SELECT query)
        """

        if self.query.strip().startswith("SELECT"):  # Modifie the query to count the number of answer

            if self.verbose:
                print(tm.strftime(f"[%H:%M:%S] Obtention du nombre de résultats avant exécuter la requête"))

            start: int = 7  # We detect the position of the first variable after the select
            while self.query[start] != '?':
                start += 1
            end: int = start
            while self.query[end] != ' ' and self.query[end] != '\n':
                end += 1

            mot: str = self.query[start: end]  # THe name of the variable

            self.sparql.setQuery(self.query.replace(mot, f"(COUNT ({mot}) as ?cnt)", 1))
            processed_results: dict = self.sparql.query().convert()  # Do the query
            number_of_results: int = int(processed_results['results']['bindings'][0]['cnt']['value'])

            if self.verbose:
                print(tm.strftime(f"[%H:%M:%S] Il y a  {number_of_results} résultats..."))

            return number_of_results
        return -1

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

        if self.verbose:
            print(tm.strftime(f" Effectué"))

        return pd.DataFrame(out, columns=cols)

    def do_query(self) -> pd.DataFrame:

        if self.resultSize > self.step:
            query = self.query + f" LIMIT {self.step}"
            return pd.concat(
                [self.get_sparql_dataframe(query + f" OFFSET {value}", f"{value:6} sur {self.resultSize}") for value in
                 range(0, self.resultSize, self.step)])

        return self.get_sparql_dataframe(self.query)
