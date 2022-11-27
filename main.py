import sqlite3

import pandas as pd


def main():
    all_data = load_all_data()


def load_all_data():
    con = sqlite3.connect("ais2022.db")
    students = pd.read_sql_query("SELECT DISTINCT id "
                                 "FROM export", con)
    students.reset_index()
    students_array = []
    for index, row in students.iterrows():
        students_array.append(row['id'])

    all_data = []

    for student in students_array:
        years_per_student = pd.read_sql_query(f"SELECT DISTINCT akrok "
                                              f"FROM export "
                                              f"WHERE id = {student} "
                                              f"ORDER BY akrok", con)
        years_per_student.reset_index()
        years_per_student_array = []
        for index, row in years_per_student.iterrows():
            years_per_student_array.append(row['akrok'])

        if len(years_per_student_array) <= 1:
            continue
        print("student", student)

        x_courses_array = []
        for year_index, year in enumerate(years_per_student_array[:-1]):
            all_data_item = []
            x_courses = pd.read_sql_query(f"SELECT idpred"
                                          f" FROM export"
                                          f" WHERE id = {student} AND akrok = '{year}'", con)
            for index, row in x_courses.iterrows():
                x_courses_array.append(row['idpred'])
            all_data_item.append(x_courses_array)

            print(year)
            print('X:', len(x_courses_array), x_courses_array)
            next_year = years_per_student_array[year_index + 1]
            y_courses = pd.read_sql_query(f"SELECT idpred"
                                          f" FROM export"
                                          f" WHERE id = {student} AND akrok = '{next_year}'", con)
            y_courses_array = []
            for index, row in y_courses.iterrows():
                y_courses_array.append(row['idpred'])
            all_data_item.append(y_courses_array)

            print('Y:', len(y_courses_array), y_courses_array)
            all_data_item.append(year)
            all_data.append(all_data_item)
        print()
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
