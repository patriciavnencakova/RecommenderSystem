import random
import sqlite3

import pandas as pd


def main():
    all_data = load_all_data("ais2022.db")
    train_data, test_data = separate_data_into_test_and_train(all_data)
    # for dato in test_data:
    #     print(dato[0])
    #     print(dato[1])
    #     print(dato[2])
    #     print()
    courses = get_courses("ais2022.db")
    model1 = RandomRS(courses)
    # print(model1.predict())


def load_all_data(database):
    con = sqlite3.connect(database)
    students = pd.read_sql_query("SELECT DISTINCT id "
                                 "FROM export", con)
    students.reset_index()
    students_array = []
    for index, row in students.iterrows():
        students_array.append(int(row['id']))

    all_data = []

    # for student in students_array:
    # len 200 studentov pre jednoduchost
    for student in random.sample(students_array, 20):
        years_per_student = pd.read_sql_query(f"SELECT DISTINCT akrok "
                                              f"FROM export "
                                              f"WHERE id = {student} "
                                              f"ORDER BY akrok", con)
        years_per_student.reset_index()
        years_per_student_array = []
        for index, row in years_per_student.iterrows():
            years_per_student_array.append(row['akrok'])

        print("student", student)

        x_courses_array = []
        for year in years_per_student_array:
            all_data_item = []
            y_courses = pd.read_sql_query(f"SELECT idpred"
                                          f" FROM export"
                                          f" WHERE id = {student} AND akrok = '{year}'", con)
            y_courses_array = []
            for index, row in y_courses.iterrows():
                y_courses_array.append(int(row['idpred']))
            all_data_item.append(x_courses_array.copy())
            all_data_item.append(y_courses_array)
            all_data_item.append(year)
            # print(all_data_item)
            all_data.append(all_data_item)
            x_courses_array.extend(y_courses_array)
        # print()
    con.close()
    return all_data


def separate_data_into_test_and_train(all_data):
    train_data = []
    test_data = []
    for dato in all_data:
        if dato[2] == '2021/22':
            test_data.append(dato)
        else:
            train_data.append(dato)
    return train_data, test_data


def get_courses(database):
    con = sqlite3.connect(database)
    courses = pd.read_sql_query("SELECT DISTINCT idpred "
                                "FROM predmet", con)
    courses_array = []
    for index, row in courses.iterrows():
        courses_array.append(int(row['idpred']))
    con.close()
    return courses_array


class RandomRS:
    def __init__(self, courses):
        self.courses = courses

    def predict(self):
        return random.sample(self.courses, 5)


#
# class TestRandomRS:
#     def test_usage(self):
#         randomRS = RandomRS(None)
#         assert False
#
#
# class TestRandomSample:
#     def test_usage(self):
#         a = [1,2,3,4,5]
#
#         for i in range(100):
#             b = random.sample(a, 3)
#             print(b)
#             assert len(b) == 3
#             assert all(x in a for x in b)
#

if __name__ == "__main__":
    main()
