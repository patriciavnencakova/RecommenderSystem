import random
import sqlite3

import numpy as np
import pandas as pd


def main():
    courses_dict = get_courses("ais2022.db")
    programs_dict = get_programs("ais2022.db")
    # print(programs_dict)
    # print(courses_dict)
    all_data = load_all_data("ais2022.db", courses_dict, programs_dict)
    # train_data, test_data = separate_data_into_test_and_train(all_data)
    model = JaccardIndexRS(courses_dict, 1)
    model.train(all_data)
    # model1 = RandomRS(courses_dict)
    evaluator = Evaluator(len(courses_dict), programs_dict, all_data)
    total_score, score_per_program_dict = evaluator.evaluate(model)
    print(total_score)
    print(score_per_program_dict)


def load_all_data(database, courses_dict, programs_dict):
    # data vo forme [mal_som_zapisane, zapisal_som, v_roku, stud_prog]
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
    # counter = 0
    # for student in students_array:
    #     if counter == 3:
    #         break
    for student in random.sample(students_array, 200):
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
            y_courses = pd.read_sql_query(f"SELECT idpred, skratkasp"
                                          f" FROM export"
                                          f" WHERE id = {student} AND akrok = '{year}'", con)
            # y_courses = predmety, ktore som zapisal
            y_courses_array = []
            program = ''
            for index, row in y_courses.iterrows():
                y_courses_array.append(courses_dict[int(row['idpred'])])
                program = row['skratkasp']
            all_data_item.append(x_courses_array.copy())
            all_data_item.append(y_courses_array)
            all_data_item.append(year)
            all_data_item.append(programs_dict[program])
            # print(all_data_item)
            all_data.append(all_data_item)
            x_courses_array.extend(y_courses_array)
        # counter += 1
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


def get_programs(database):
    # zoberieme studijne programy, ktore nie su doktorandske
    con = sqlite3.connect(database)
    programs = pd.read_sql_query("SELECT skratkasp "
                                 "FROM studprog ", con)
    programs_dict = {}
    counter = 0
    for index, row in programs.iterrows():
        program = row['skratkasp']
        if program[0] != 'd':
            programs_dict[program] = counter
            counter = counter + 1
    con.close()
    return programs_dict


class Evaluator:
    def __init__(self, number_of_courses, programs_dict, test_data):
        self.number_of_courses = number_of_courses
        self.programs_dict = programs_dict
        self.test_data = test_data

    def evaluate(self, trained_model):
        RMSEs = []
        programs_RMSEs = []
        for i in range(len(self.programs_dict)):
            programs_RMSEs.append([])
        for data in self.test_data:
            # chcem predikovat predmety, ktore som skutocne zapisal
            reality = data[1]
            # na predikovanie posielam len predmety, ktore som mal zapisane -> pouzijeme data[0]
            prediction = trained_model.predict(data)
            RMSE = 0
            for i in range(self.number_of_courses):
                if i in reality:
                    RMSE += np.power(prediction[i] - 1, 2)
                else:
                    RMSE += np.power(prediction[i], 2)
            RMSE /= self.number_of_courses
            RMSE = np.sqrt(RMSE)
            RMSEs.append(RMSE)
            programs_RMSEs[data[3]].append(RMSE)
        total_score = np.sum(RMSEs)
        total_score /= len(self.test_data)
        score_per_program_dict = {}
        keys = [k for k, v in self.programs_dict.items()]
        for i in range(len(programs_RMSEs)):
            if len(programs_RMSEs[i]) == 0:
                score_per_program_dict[keys[i]] = 0
                continue
            score = np.sum(programs_RMSEs[i])
            score /= len(programs_RMSEs[i])
            score_per_program_dict[keys[i]] = score
        return total_score, score_per_program_dict


class RandomRS:
    def __init__(self, courses):
        self.courses = courses

    def predict(self, data):
        result = list()
        for i in range(len(self.courses)):
            result.append(random.uniform(0, 1))
        return result


class JaccardIndexRS:
    def __init__(self, courses, n):
        self.data = None
        self.courses = courses
        self.n = n

    def train(self, train_data):
        self.data = train_data

    def predict(self, data):
        # vrati zoznam pravdepodobnosti, zapisania predmetov
        s1 = set(data[0])
        tuples = list()
        for dato in self.data:
            s2 = set(dato[0])
            jaccard_index = 0
            if len(s1) == 0 and len(s2) == 0:
                if data[3] == dato[3]:
                    jaccard_index = 1.0
            else:
                jaccard_index = len(s1.intersection(s2)) / len(s1.union(s2))
            # tuple vo formate (podobnost, predemty_na_zapisanie)
            our_tuple = (jaccard_index, dato[1])
            tuples.append(our_tuple)
        tuples.sort(reverse=True)
        # print(tuples)
        top_n = tuples[:self.n]
        # print(top_n)
        result = list()
        for i in range(len(self.courses)):
            counter = 0
            for dato in top_n:
                if i in dato[1]:
                    counter += 1
            result.append(counter / self.n)

        # for i in range(len(result)):
        #     if result[i] != 0:
        #         print(f"{i}: {result[i]}")
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
