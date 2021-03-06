"""The file "data_prep_pi.py" cleans the data from
SAINC1_1998_2017_ALL_AREAS.csv. It prepares the dataset we use for
further analysis.

Data source: U.S. Department of Commerce / Bureau of Economic Analysis /
Regional Economic Accounts

"""


import numpy as np
import pandas as pd
import json

from bld.project_paths import project_paths_join as ppj
from src.model_code.data_cleaner import data_cleaner, lag_generator


def save_data(sample):
    """Save cleaned data as .dta file."""
    sample.to_stata(ppj("OUT_DATA", "pi.dta"))


if __name__ == "__main__":
    state_names = json.load(open(ppj("IN_MODEL_SPECS", "state_names.json"),
                                 encoding="utf-8"))
    data = pd.read_csv(ppj("IN_DATA", "SAINC1_1998_2017_ALL_AREAS.csv"),
                       encoding="ISO-8859-1")

    excluded_years = [str(i) for i in list(range(1998, 2007, 1))]
    data.drop(columns=excluded_years, inplace=True)
    data.drop(columns=['GeoFIPS', 'Region', 'TableName', 'Unit',
                       'IndustryClassification', 'Description'], inplace=True)
    data.dropna(inplace=True)

    data = data_cleaner(data, 'GeoName', state_names)

    data = pd.wide_to_long(data,
                           ['20'],
                           i=['GeoName', 'LineCode'],
                           j='year').reset_index()
    data = data.set_index(['GeoName',
                           'year',
                           'LineCode']).unstack().reset_index()
    data.columns = data.columns.map('{0[0]}{0[1]}'.format)

    data.rename(columns={'GeoName': 'state',
                         '201.0': 'pi',
                         '202.0': 'population',
                         '203.0': 'pi_pc'}, inplace=True)
    data['year'] = data['year'].astype(np.int) + 2000
    data['income'] = data['pi_pc'] / 1000
    data = lag_generator(data, 'income', 'year', 'state')

    save_data(data)
