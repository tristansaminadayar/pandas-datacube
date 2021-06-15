import time as tm
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from SPARQLWrapper import SPARQLWrapper


def get_sparql_dataframe(service: str, query: str, verbose: bool = False, text: str = "") -> pd.DataFrame:
    """
    Helper function to convert SPARQL results into a Pandas data frame.


    Credit: Douglas Fils

    :param text: An optional text to add in the verbose mode
    :param service: The link of the SPARQL service
    :param query: The content of the query
    :param verbose: If the function displays informations about execution
    :return: A data frame with the answer of the server
    """

    if verbose:
        print(tm.strftime(f"[%H:%M:%S] Transmission {text} en cours..."), end='')

    sparql = SPARQLWrapper(service)
    sparql.setQuery(query)
    sparql.setReturnFormat("json")
    processed_results: dict = sparql.query().convert()

    if verbose:
        print(tm.strftime(f"\r[%H:%M:%S] Transmission {text} réussi, conversion en Data Frame..."), end='')

    cols = processed_results['head']['vars']
    out: list = []
    for row in processed_results['results']['bindings']:
        item: list = []
        for c in cols:
            item.append(row.get(c, {}).get('value'))
        out.append(item)

    if verbose:
        print(tm.strftime(f" Effectué"))

    return pd.DataFrame(out, columns=cols)


def get_sparql_dataframe_complete(service: str, query: str, verbose: bool = False, step: int = 5000) -> pd.DataFrame:
    """
    When in SELECTION mode, if the number of results is too high, the server is interrogated progressively

    :param service: The link of the SPARQL service
    :param query: The content of the query
    :param verbose: If the function displays informations about execution
    :param step: The max number of one query
    :return: A data frame with the answer of the server
    """

    sparql = SPARQLWrapper(service)
    sparql.setReturnFormat("json")

    if query.strip().startswith("SELECT"):  # Modifie the query to count the number of answer

        if verbose:
            print(tm.strftime(f"[%H:%M:%S] Verification du nombre de résultats avant le requête"))

        start: int = 7
        while query[start] != '?':
            start += 1
        end: int = start
        while query[end] != ' ' and query[end] != '\n':
            end += 1
        mot: str = query[start: end]
        query_number: str = query.replace(mot, f"(COUNT (*) as ?cnt)", 1)
        sparql.setQuery(query_number)
        processed_results: dict = sparql.query().convert()
        number_of_results: int = int(processed_results['results']['bindings'][0]['cnt']['value'])

        if verbose:
            print(tm.strftime(f"[%H:%M:%S] Téléchargement de {number_of_results} résultats..."))

        if number_of_results > step:
            query += f" LIMIT {step}"
            return pd.concat([get_sparql_dataframe(service, query + f" OFFSET {value}", verbose,
                                                   f"{value:6} sur {number_of_results}") for value in
                              range(0, number_of_results, step)])

    return get_sparql_dataframe(service, query, verbose)


endpoint: str = "http://kaiko.getalp.org/sparql"
statement: str = """SELECT DISTINCT ?t WHERE {?t a qb:DataSet }"""

list_datasets = get_sparql_dataframe_complete(endpoint, statement).values.reshape(
    -1)  # We recovers all DataSets Structure

obs: dict = {}
for dataset in list_datasets:
    statement: str = f"""SELECT DISTINCT ?obs WHERE {'{'} ?obs qb:dataSet <{dataset}> {'}'}"""
    result = get_sparql_dataframe_complete(endpoint, statement).values.reshape(-1)
    name = dataset.split('/')[-1]
    obs[name] = result

STEP = 50
DataFrames: dict = {}

total: int = sum([len(item) for item in obs.values()])
val: int = 0
for key, values in zip(obs.keys(), obs.values()):
    size: int = len(values)
    tab: list = []
    for i in range(0, size, STEP):
        statement = f"DESCRIBE "
        maxi: int = i + STEP
        if maxi > size:
            maxi = size
        for uri in values[i:maxi]:
            statement += "<" + uri + "> "
        result = get_sparql_dataframe(endpoint, statement).sort_values(by='p').sort_values(by='s')[['p', 'o']].values
        line_per_observation: int = result.shape[0] // (maxi - i)
        for j in range(0, result.shape[0], line_per_observation):
            temp = result[j:j + line_per_observation].T
            a = pd.DataFrame(data=[list(temp[1])], columns=list(temp[0]))
            tab.append(a)
        val += (maxi - i)
        print(tm.strftime(f"\r[%H:%M:%S] Téléchargement de {i} / {size} résultats... "), end='')
    print("\nFusion de la base de donnée...")
    DataFrames[key] = pd.concat(tab)

for key in DataFrames.keys():
    DataFrames[key].to_csv(f"{key}_brut.csv")

DataFrames["dbnaryStatisticsCube"] = pd.read_csv("dbnaryStatisticsCube_brut.csv", header=0, index_col=0)


def transformation_date(date: int) -> str:
    date = str(date)
    return date[:4] + '-' + date[4:6] + '-' + date[6:8]


for key in DataFrames.keys():
    DataFrames[key] = DataFrames[key].rename(columns=lambda item: item.split('#')[-1])
    DataFrames[key]["wiktionaryDumpVersion"] = DataFrames[key]["wiktionaryDumpVersion"].map(transformation_date)

data = DataFrames["dbnaryStatisticsCube"]

sns.set_theme(style="darkgrid")

fig = plt.figure(dpi=200)
plot_ = sns.lineplot(data=data[data["observationLanguage"] == "fr"], x="wiktionaryDumpVersion", y="translationsCount")
sns.lineplot(data=data[data["observationLanguage"] == "fr"], x="wiktionaryDumpVersion", y="lexicalEntryCount")
sns.lineplot(data=data[data["observationLanguage"] == "fr"], x="wiktionaryDumpVersion", y="lexicalSenseCount")
sns.lineplot(data=data[data["observationLanguage"] == "fr"], x="wiktionaryDumpVersion", y="pageCount")
plt.xticks(rotation=25)
y_labels = plot_.get_yticks()
plot_.set_yticklabels([int(y) for y in y_labels])
for ind, label in enumerate(plot_.get_xticklabels()):
    if ind % 20 == 0:  # every 10th label is kept
        label.set_visible(True)
    else:
        label.set_visible(False)
