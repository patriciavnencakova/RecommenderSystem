import random
import sqlite3

import numpy as np
import pandas as pd
import sys as s


def main():
    # file1 = open("score_JaccardIndexRS_n1.txt", "x")
    # file2 = open("score_JaccardIndexRS_n10.txt", "x")
    # file3 = open("score_JaccardIndexRS_n20.txt", "x")
    # file4 = open("score_JaccardIndexRS_n100.txt", "x")
    # file5 = open("score_RandomRS.txt", "x")
    programs_dict = get_programs("ais2022.db")
    courses_dict, courses_dict_names = get_courses("ais2022.db")
    print('pocet predmetov pred zlucenim:', len(courses_dict))
    same_courses = merge_same_courses("ais2022.db", courses_dict)
    print('pocet predmetov po zluceni:', len(same_courses))

    doctoral_courses = get_doctoral_courses("ais2022.db", courses_dict)
    print('doktorandske predmety:', len(doctoral_courses))
    # print(redundant_courses)

    only_one_enrollment_courses = get_courses_with_only_one_enrollment("ais2022.db", courses_dict)
    print('predmety, ktore boli zapisane len jedenkrat:', len(only_one_enrollment_courses))
    # print(only_one_enrollment_courses)

    redundant_courses = doctoral_courses.union(only_one_enrollment_courses)
    print('celkovo predmety, ktore nezapocitavame:', len(redundant_courses))
    # print(redundant_courses)

    RMSE_courses = len(same_courses) - len(redundant_courses)
    print('predmety, ktore idu do RMSE:', RMSE_courses)

    # all_data = load_all_data("ais2022.db", courses_dict, programs_dict)
    # 13 roznych akademickych rokov
    # train_data, test_data = separate_data_into_test_and_train("ais2022.db", all_data, 3)
    # evaluator = Evaluator(len(courses_dict), RMSE_courses, programs_dict, test_data)

    # JI = JaccardIndexRS(courses_dict, redundant_courses, 10)
    # JI.train(train_data)
    # my_data = my_data = [[1783, 1569, 1873, 4259, 1931, 174, 1733, 1526, 3485, 3447, 1302, 1871, 1874, 8, 4411, 182,
    #                       1734, 1533], [], '2021/22', 'INF']
    # JI.predict(my_data)

    # RS1 = JaccardIndexRS(courses_dict, redundant_courses, 1)
    # RS1.train(train_data)
    # total_score, score_per_program_dict = evaluator.evaluate(RS1)
    # file1.write(str(total_score))
    # file1.write("{\n")
    # for k in score_per_program_dict.keys():
    #     file1.write(F"'{k}': '{score_per_program_dict[k]}',\n")  # add comma at end of line
    # file1.write("}")
    # print(total_score)
    # print(score_per_program_dict)
    #
    # RS2 = JaccardIndexRS(courses_dict, redundant_courses, 10)
    # RS2.train(train_data)
    # total_score, score_per_program_dict = evaluator.evaluate(RS2)
    # file2.write(str(total_score))
    # file2.write("{\n")
    # for k in score_per_program_dict.keys():
    #     file2.write(F"'{k}': '{score_per_program_dict[k]}',\n")  # add comma at end of line
    # file2.write("}")
    # print(total_score)
    # print(score_per_program_dict)
    #
    # RS3 = JaccardIndexRS(courses_dict, redundant_courses, 20)
    # RS3.train(train_data)
    # total_score, score_per_program_dict = evaluator.evaluate(RS3)
    # file3.write(str(total_score))
    # file3.write("{\n")
    # for k in score_per_program_dict.keys():
    #     file3.write(F"'{k}': '{score_per_program_dict[k]}',\n")  # add comma at end of line
    # file3.write("}")
    # print(total_score)
    # print(score_per_program_dict)
    #
    # RS4 = JaccardIndexRS(courses_dict, redundant_courses, 100)
    # RS4.train(train_data)
    # total_score, score_per_program_dict = evaluator.evaluate(RS4)
    # file4.write(str(total_score))
    # file4.write("{\n")
    # for k in score_per_program_dict.keys():
    #     file4.write(F"'{k}': '{score_per_program_dict[k]}',\n")  # add comma at end of line
    # file4.write("}")
    # print(total_score)
    # print(score_per_program_dict)
    #
    # RS5 = RandomRS(courses_dict, redundant_courses)
    # total_score, score_per_program_dict = evaluator.evaluate(RS5)
    # file5.write(str(total_score))
    # file5.write("{\n")
    # for k in score_per_program_dict.keys():
    #     file5.write(F"'{k}': '{score_per_program_dict[k]}',\n")  # add comma at end of line
    # file5.write("}")
    # print(total_score)
    # print(score_per_program_dict)


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

    for student in students_array:
        # len 200 studentov pre jednoduchost
        # counter = 0
        # for student in students_array:
        #     if counter == 3:
        #         break
        # for student in random.sample(students_array, 200):
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


def separate_data_into_test_and_train(database, all_data, number_of_tested_years):
    con = sqlite3.connect(database)
    years = pd.read_sql_query("SELECT DISTINCT akrok FROM export ORDER BY akrok DESC", con)
    years.reset_index()
    years_array = []
    for index, row in years.iterrows():
        years_array.append(row['akrok'])
    train_data = []
    test_data = []
    # print(years_array[:number_of_tested_years])
    for dato in all_data:
        # if dato[2] == '2021/22':
        # zoberieme poslednych number_of_tested_years rokov za testovacie
        if dato[2] in years_array[:number_of_tested_years]:
            test_data.append(dato)
        else:
            train_data.append(dato)
    return train_data, test_data


def get_courses(database):
    # zoberieme predmety, ktore nie su doktorandske
    con = sqlite3.connect(database)
    courses = pd.read_sql_query(
        """SELECT DISTINCT idpred, nazovpred, skratkapred
        FROM predmet
        ORDER BY idpred""", con)

    courses_dict = {}
    courses_dict_names = {}
    counter = 0
    for index, row in courses.iterrows():
        # preindexovanie id predmetov
        if int(row['idpred']) in courses_dict.keys():
            continue
        courses_dict[int(row['idpred'])] = counter
        courses_dict_names[int(row['idpred'])] = row['nazovpred']
        counter += 1
    con.close()
    return courses_dict, courses_dict_names


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


# mam povodne id
def get_old_courses(database, courses_dict):
    con = sqlite3.connect(database)
    old_courses = pd.read_sql_query("SELECT DISTINCT idpred "
                                    "FROM export "
                                    "WHERE idpred NOT IN ( "
                                    "SELECT DISTINCT idpred "
                                    "FROM export "
                                    "WHERE akrok IN ('2019/20', '2020/21', '2021/22'))", con)
    old_courses.reset_index()
    old_courses_array = []
    for index, row in old_courses.iterrows():
        old_courses_array.append(courses_dict[int(row['idpred'])])
    con.close()
    return old_courses_array


def merge_same_courses(database, courses_dict):
    con = sqlite3.connect(database)
    courses = pd.read_sql_query("SELECT * "
                                "FROM predmet", con)
    duplicate_courses_dict = {}
    for index, row in courses.iterrows():
        # ak je rovnaka skratka a zaroven nazov, tak ich zlucim
        key = f"{row['skratkapred']}_{row['nazovpred']}"
        parts = row['kodpred'].split("/")
        # course = courses_dict[int(row['idpred'])]
        if key in duplicate_courses_dict:
            value = duplicate_courses_dict[key]
            # najaktualnejsia verzia je ta, ktora ma najvacsie cislo v kode predmetu
            if value['max_value'] < int(parts[-1]):
                value['max_value'] = int(parts[-1])
                value['max_id'] = courses_dict[int(row['idpred'])]
            value['courses'].append(int(row['idpred']))
        else:
            value = {
                'max_value': int(parts[-1]),
                'max_id': courses_dict[int(row['idpred'])],
                'courses': [int(row['idpred'])]
            }
            duplicate_courses_dict[key] = value

    for key, value in duplicate_courses_dict.items():
        for course in value['courses']:
            courses_dict[course] = value['max_id']
    con.close()
    return duplicate_courses_dict


def get_courses_with_only_one_enrollment(database, courses_dict):
    con = sqlite3.connect(database)
    courses = pd.read_sql_query("""select * FROM predmet
                                where predmet.idpred in
                                (SELECT export.idpred
                                FROM export
                                GROUP BY export.idpred
                                HAVING COUNT(export.idpred) = 1)""", con)
    only_one_enrollment_courses = set()
    for index, row in courses.iterrows():
        only_one_enrollment_courses.add(courses_dict[int(row['idpred'])])
    con.close()
    return only_one_enrollment_courses


def get_doctoral_courses(database, courses_dict):
    con = sqlite3.connect(database)
    doctoral = pd.read_sql_query(
        """SELECT *
        FROM predmet""", con)
    doctoral_courses = set()
    for index, row in doctoral.iterrows():
        course = row['skratkapred']
        if course.startswith('3-'):
            doctoral_courses.add(courses_dict[int(row['idpred'])])
    con.close()
    return doctoral_courses


class Evaluator:
    def __init__(self, number_of_courses, RMSE_courses, programs_dict, test_data):
        self.number_of_courses = number_of_courses
        self.RMSE_courses = RMSE_courses
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
            counter = 0
            for i in range(self.number_of_courses):
                if i in reality:
                    RMSE += np.power(prediction[i] - 1, 2)
                    counter += 1
                else:
                    if prediction[i] != 0:
                        counter += 1
                    RMSE += np.power(prediction[i], 2)
            # RMSE /= self.RMSE_courses
            RMSE /= counter
            RMSE = np.sqrt(RMSE)
            RMSEs.append(RMSE)
            programs_RMSEs[data[3]].append(RMSE)
        total_score = np.sum(RMSEs)
        total_score /= len(self.test_data)
        score_per_program_dict = {}
        keys = [k for k, v in self.programs_dict.items()]
        for i in range(len(programs_RMSEs)):
            if len(programs_RMSEs[i]) == 0:
                score_per_program_dict[keys[i]] = None
                continue
            score = np.sum(programs_RMSEs[i])
            score /= len(programs_RMSEs[i])
            score_per_program_dict[keys[i]] = score
        return total_score, score_per_program_dict


class RandomRS:
    def __init__(self, courses, redundant_courses):
        self.courses = courses
        self.redundant_courses = redundant_courses

    def predict(self, data):
        result = list()
        for i in range(len(self.courses)):
            if i in self.redundant_courses:
                result.append(0)
                continue
            result.append(random.uniform(0, 1))
        return result


class JaccardIndexRS:
    def __init__(self, courses, redundant_courses, n):
        self.data = None
        self.courses = courses
        self.redundant_courses = redundant_courses
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
            if i in self.redundant_courses or i in s1:
                result.append(0)
                continue
            counter = 0
            for dato in top_n:
                if i in dato[1]:
                    counter += 1
            result.append(counter / self.n)

        # for i in range(len(result)):
        #     if result[i] != 0:
        #         print(f"{i}: {result[i]}")
        return result


# hamming distance = pocet rozdielnych => cim menej rozdielnych, tym lepsie
class HammingDistanceRS:
    def __init__(self, courses, redundant_courses, n):
        self.data = None
        self.courses = courses
        self.redundant_courses = redundant_courses
        self.n = n

    def train(self, train_data):
        self.data = train_data

    def predict(self, data):
        # vrati zoznam pravdepodobnosti, zapisania predmetov
        s1 = set(data[0])
        tuples = list()
        for dato in self.data:
            s2 = set(dato[0])
            hamming_distance = 0
            if len(s1) == 0 and len(s2) == 0:
                if data[3] == dato[3]:
                    hamming_distance = 0
            else:
                hamming_distance = len(s1) + len(s2) - 2 * len(s1.intersection(s2))
            # tuple vo formate (pocet_rozdielnych, predemty_na_zapisanie)
            our_tuple = (hamming_distance, dato[1])
            tuples.append(our_tuple)
        tuples.sort()
        # print(tuples)
        top_n = tuples[:self.n]
        # print(top_n)
        result = list()
        for i in range(len(self.courses)):
            if i in self.redundant_courses or i in s1:
                result.append(0)
                continue
            counter = 0
            for dato in top_n:
                if i in dato[1]:
                    counter += 1
            result.append(counter / self.n)

        # for i in range(len(result)):
        #     if result[i] != 0:
        #         print(f"{i}: {result[i]}")
        return result


# prienik => cim viac spolocnych, tym lepsie
class IntersectionRS:
    def __init__(self, courses, redundant_courses, n):
        self.data = None
        self.courses = courses
        self.redundant_courses = redundant_courses
        self.n = n

    def train(self, train_data):
        self.data = train_data

    def predict(self, data):
        # vrati zoznam pravdepodobnosti, zapisania predmetov
        s1 = set(data[0])
        tuples = list()
        for dato in self.data:
            s2 = set(dato[0])
            intersection = 0
            if len(s1) == 0 and len(s2) == 0:
                if data[3] == dato[3]:
                    intersection = s.maxsize
            else:
                intersection = len(s1.intersection(s2))
            # tuple vo formate (pocet_rozdielnych, predemty_na_zapisanie)
            our_tuple = (intersection, dato[1])
            tuples.append(our_tuple)
        tuples.sort(reverse=True)
        # print(tuples)
        top_n = tuples[:self.n]
        # print(top_n)
        result = list()
        for i in range(len(self.courses)):
            if i in self.redundant_courses or i in s1:
                result.append(0)
                continue
            counter = 0
            for dato in top_n:
                if i in dato[1]:
                    counter += 1
            result.append(counter / self.n)

        # for i in range(len(result)):
        #     if result[i] != 0:
        #         print(f"{i}: {result[i]}")
        return result


if __name__ == "__main__":
    main()
