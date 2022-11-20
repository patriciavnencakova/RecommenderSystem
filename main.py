import sqlite3

import pandas as pd
from IPython.display import display


def main():
    all_data = load_all_data()
    display(all_data)
    test_data = get_test_data(all_data)
    display(test_data)
    train_data = get_train_data(all_data)
    display(train_data)


def load_all_data():
    con = sqlite3.connect("ais2022.db")
    all_data = pd.read_sql_query("SELECT * FROM export", con)
    con.close()
    return all_data


def get_test_data(all_data):
    test_data = all_data[all_data.akrok == '2021/22']
    return test_data


def get_train_data(all_data):
    test_data = all_data[all_data.akrok != '2021/22']
    return test_data


def get_matrix_from_data(data):
    # TODO: z dat vyrobit maticu (ak vobec treba)
    matrix = data
    return matrix


if __name__ == "__main__":
    main()
