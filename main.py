import random
import sqlite3

import numpy as np
import pandas as pd


def main():
    courses_dict = get_courses("ais2022.db")
    all_data = load_all_data("ais2022.db", courses_dict)
    train_data, test_data = separate_data_into_test_and_train(all_data)
    model1 = RandomRS(courses_dict)
    evaluator = Evaluator(len(courses_dict), test_data)
    score = evaluator.evaluate(model1, test_data)
    print(score)


def load_all_data(database, courses_dict):
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

        # print("student", student)
        # x_courses = predmety, ktore som mal
        x_courses_array = []
        for year in years_per_student_array:
            all_data_item = []
            y_courses = pd.read_sql_query(f"SELECT idpred"
                                          f" FROM export"
                                          f" WHERE id = {student} AND akrok = '{year}'", con)
            # y_courses = predmety, ktore som zapisal
            y_courses_array = []
            for index, row in y_courses.iterrows():
                y_courses_array.append(courses_dict[int(row['idpred'])])
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
                                "FROM predmet "
                                "ORDER BY idpred", con)
    courses_dict = {}
    for index, row in courses.iterrows():
        # preindexovanie id predmetov
        courses_dict[int(row['idpred'])] = index
    con.close()
    return courses_dict

class Evaluator:
    def __init__(self, number_of_courses, test_data):
        self.number_of_courses = number_of_courses
        self.test_data = test_data

    def evaluate(self, trained_model, test_data):
        RMSEs = []
        for data in test_data:
            # chcem predikovat predmety, ktore som skutocne zapisal
            reality = data[1]
            # na predikovanie posielam len predmety, ktore som mal zapisane
            prediction = trained_model.predict(data[0])
            RMSE = 0
            for i in range(self.number_of_courses):
                if i in reality:
                    RMSE += np.power(prediction[i] - 1, 2)
                else:
                    RMSE += np.power(prediction[i], 2)
            RMSE /= self.number_of_courses
            RMSE = np.sqrt(RMSE)
            RMSEs.append(RMSE)
        result = np.sum(RMSEs)
        result /= len(test_data)
        return result


class RandomRS:
    def __init__(self, courses):
        self.courses = courses

    def predict(self, data):
        result = list()
        for i in range(len(self.courses)):
            result.append(random.uniform(0, 1))
        return result


# class TestRandomRS:
#     def test_usage(self):
#         randomRS = RandomRS(None)
#         assert False


# class TestRandomSample:
#     def test_usage(self):
#         a = [1,2,3,4,5]

# for i in range(100):
#     b = random.sample(a, 3)
#     print(b)
#     assert len(b) == 3
#     assert all(x in a for x in b)


if __name__ == "__main__":
    main()
