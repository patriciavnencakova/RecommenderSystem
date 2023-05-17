import random
import sqlite3

import sys as s
from typing import Tuple
import numpy as np
import pandas as pd

from all_data import ALL_DATA


def main():
    file1 = open("score_JaccardIndexRS_09,10_21.txt", "w")
    file2 = open("score_HammingDistanceRS_09,10_21.txt", "w")
    file3 = open("score_IntersectionRS_09,10_21.txt", "w")

    programs_dict, fields_division = get_programs("ais2022.db")
    print(len(programs_dict))
    # print(programs_dict)
    # print(len(fields_division))
    # print(fields_division)
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

    all_data = ALL_DATA
    # print(len(ALL_DATA))

    # all_data = load_all_data("ais2022.db", courses_dict, programs_dict)
    # print(all_data)

    # 13 roznych akademickych rokov
    train_years = ['2009/10', '2010/11']
    test_years = ['2021/22']
    train_data, test_data = separate_data_into_test_and_train("ais2022.db", all_data, train_years, test_years)
    evaluator = Evaluator(len(courses_dict), RMSE_courses, fields_division, test_data)

    # JI = JaccardIndexRS(courses_dict, redundant_courses, 10)
    # JI.train(train_data)
    # my_data = my_data = [[1783, 1569, 1873, 4259, 1931, 174, 1733, 1526, 3485, 3447, 1302, 1871, 1874, 8, 4411, 182,
    #                       1734, 1533], [], '2021/22', 'INF']
    # JI.predict(my_data)

    RS1 = JaccardIndexRS(courses_dict, redundant_courses, 15)
    RS1.train(train_data)
    total_score, score_per_program_dict = evaluator.evaluate(RS1)
    file1.write(str(total_score))
    file1.write("{\n")
    for k in score_per_program_dict.keys():
        file1.write(F"'{k}': '{score_per_program_dict[k]}',\n")  # add comma at end of line
    file1.write("}")
    print(total_score)
    print(score_per_program_dict)

    RS2 = HammingDistanceRS(courses_dict, redundant_courses, 15)
    RS2.train(train_data)
    total_score, score_per_program_dict = evaluator.evaluate(RS2)
    file2.write(str(total_score))
    file2.write("{\n")
    for k in score_per_program_dict.keys():
        file2.write(F"'{k}': '{score_per_program_dict[k]}',\n")  # add comma at end of line
    file2.write("}")
    print(total_score)
    print(score_per_program_dict)

    RS3 = IntersectionRS(courses_dict, redundant_courses, 15)
    RS3.train(train_data)
    total_score, score_per_program_dict = evaluator.evaluate(RS3)
    file3.write(str(total_score))
    file3.write("{\n")
    for k in score_per_program_dict.keys():
        file3.write(F"'{k}': '{score_per_program_dict[k]}',\n")  # add comma at end of line
    file3.write("}")
    print(total_score)
    print(score_per_program_dict)


def load_all_data(database: str, courses: dict, programs: dict) -> list:
    # data vo forme [mal_som_zapisane, zapisal_som, v_roku, stud_prog]
    con = sqlite3.connect(database)
    students_rows = pd.read_sql_query("SELECT DISTINCT id FROM export", con)
    students_rows.reset_index()
    students = []
    for index, row in students_rows.iterrows():
        students.append(int(row['id']))

    all_data = []

    for student in students:
        # len 200 studentov pre jednoduchost
        # counter = 0
        # for student in students:
        #     if counter == 3:
        #         break
        # for student in random.sample(students, 200):
        years_per_student_rows = pd.read_sql_query(f"SELECT DISTINCT akrok "
                                                   f"FROM export "
                                                   f"WHERE id = {student} "
                                                   f"ORDER BY akrok", con)
        years_per_student_rows.reset_index()
        years_per_student = []
        for index, row in years_per_student_rows.iterrows():
            years_per_student.append(row['akrok'])

        # print("student", student)
        # x_courses = predmety, ktore som mal
        x_courses = []
        for year in years_per_student:
            all_data_item = []
            y_courses_rows = pd.read_sql_query(f"SELECT idpred, skratkasp"
                                               f" FROM export"
                                               f" WHERE id = {student} AND akrok = '{year}'", con)
            # y_courses_rows = predmety, ktore som zapisal
            y_courses = []
            program = str()
            for index, row in y_courses_rows.iterrows():
                y_courses.append(courses[int(row['idpred'])])
                program = row['skratkasp']
            # all_data_item.append(x_courses.copy())
            # all_data_item.append(y_courses)
            # all_data_item.append(year)
            # all_data_item.append(programs[program])
            # # print(all_data_item)
            all_data_item.extend([x_courses.copy(), y_courses, year, program])
            all_data.append(all_data_item)
            x_courses.extend(y_courses)
        # counter += 1
        # print()
    con.close()
    return all_data


def separate_data_into_test_and_train(
        database: str,
        all_data: list,
        train_years: list,
        test_years: list
) -> Tuple[list, list]:
    con = sqlite3.connect(database)
    years_rows = pd.read_sql_query("SELECT DISTINCT akrok FROM export ORDER BY akrok DESC", con)
    years_rows.reset_index()
    years = []
    for index, row in years_rows.iterrows():
        years.append(row['akrok'])
    train_data = []
    test_data = []
    # print(years[:number_of_tested_years])
    for entry in all_data:
        if entry[2] in test_years:
            test_data.append(entry)
        if entry[2] in train_years:
            train_data.append(entry)
        # if entry[2] == '2021/22':
        # zoberieme poslednych number_of_tested_years rokov za testovacie
        # if entry[2] in years[:number_of_tested_years]:
        #     test_data.append(entry)
        # else:
        #     train_data.append(entry)
    return train_data, test_data


def get_courses(database: str) -> Tuple[dict, dict]:
    # zoberieme predmety, ktore nie su doktorandske
    con = sqlite3.connect(database)
    courses_rows = pd.read_sql_query(
        """SELECT DISTINCT idpred, nazovpred, skratkapred
        FROM predmet
        ORDER BY idpred""", con)

    courses = {}
    courses_names = {}
    counter = 0
    for index, row in courses_rows.iterrows():
        # preindexovanie id predmetov
        idpred = int(row['idpred'])
        if idpred in courses.keys():
            continue
        courses[idpred] = counter
        courses_names[idpred] = row['nazovpred']
        counter += 1
    con.close()
    return courses, courses_names


def get_programs(database: str) -> Tuple[dict, dict]:
    # zoberieme studijne programy, ktore nie su doktorandske
    con = sqlite3.connect(database)
    programs_rows = pd.read_sql_query("SELECT DISTINCT skratkasp "
                                      "FROM export ", con)
    programs = {}
    for index, row in programs_rows.iterrows():
        programs[row['skratkasp']] = index
    con.close()
    # 1 = MAT_b, 2 = INF_b, 3 = FYZ_b, 4 = UCITELSTVO_b, 5 = MAT_m, 6 = INF_m, 7 = FYZ_m, 8 = UCITELSTVO_m
    fields_division = {'MAT': 1, 'PMA': 1, 'INF': 2, 'mMMN': 5, 'MMN': 1, 'AIN': 2, 'mFFP': 7, 'FYZ': 3, 'muMAFY': 8,
                       'BMF': 3, 'mAIN': 6, 'mMAT': 5, 'mEOM': 7, 'OZE': 3, 'mINF': 6, 'EFM': 1, 'mFBM': 7, 'muMAIN': 8,
                       'upMAIN': 4, 'mFBF': 7, 'upMAFY': 4, 'mIKV': 6, 'mEMM': 5, 'upINAN': 4, 'mPMS': 5, 'mFTF': 7,
                       'mEFM': 5, 'mFTL': 7, 'mMPG': 5, 'mFFZ': 7, 'BIN': 2, 'mAIN/k': 6, 'DAV': 2, 'muMAFY/k': 8,
                       'mFJF': 7, 'muMADG': 8, 'upMADG': 4, 'mIKVa': 6, 'muMATV': 8, 'upMATV': 4, 'mINF/k': 6,
                       'mFAA': 7, 'muMAIN/k': 8, 'FYZ/k': 3, 'mAINa': 6, 'mFOS': 7, 'mFPE': 7, 'mFMK': 7, 'mINFa': 6,
                       'mFOZ': 7, 'muMADG/k': 8, 'TEF': 3, 'DAV/k': 2, 'mFTFa': 7, 'muFYIN': 8, 'upFYIN': 4,
                       'upINBI': 8, 'mMATa': 5, 'AINa': 2, 'BIN/k': 2, 'mINFa/k': 6, 'OZE/k': 3, 'mMPGa': 5, 'mEOMa': 7,
                       'TEF/k': 3, 'mFJFa': 7, 'muINBI': 4, 'FYZa': 3}
    return programs, fields_division


# mam povodne id
def get_old_courses(database: str, courses: dict) -> list:
    con = sqlite3.connect(database)
    old_courses_rows = pd.read_sql_query("SELECT DISTINCT idpred "
                                         "FROM export "
                                         "WHERE idpred NOT IN ( "
                                         "SELECT DISTINCT idpred "
                                         "FROM export "
                                         "WHERE akrok IN ('2019/20', '2020/21', '2021/22'))", con)
    old_courses_rows.reset_index()
    old_courses = []
    for index, row in old_courses_rows.iterrows():
        old_courses.append(courses[int(row['idpred'])])
    con.close()
    return old_courses


def merge_same_courses(database: str, courses: dict) -> dict:
    con = sqlite3.connect(database)
    courses_rows = pd.read_sql_query("SELECT * FROM predmet", con)
    duplicate_courses = {}
    for index, row in courses_rows.iterrows():
        # ak je rovnaka skratka a zaroven nazov, tak ich zlucim
        key = f"{row['skratkapred']}_{row['nazovpred']}"
        parts = row['kodpred'].split("/")
        # course = courses_dict[int(row['idpred'])]
        idpred = int(row['idpred'])
        if key in duplicate_courses:
            value = duplicate_courses[key]
            # najaktualnejsia verzia je ta, ktora ma najvacsie cislo v kode predmetu
            if value['max_value'] < int(parts[-1]):
                value['max_value'] = int(parts[-1])
                value['max_id'] = courses[idpred]
            value['courses'].append(idpred)
        else:
            value = {
                'max_value': int(parts[-1]),
                'max_id': courses[idpred],
                'courses': [idpred]
            }
            duplicate_courses[key] = value

    for key, value in duplicate_courses.items():
        for course in value['courses']:
            courses[course] = value['max_id']
    con.close()
    return duplicate_courses


def get_courses_with_only_one_enrollment(database: str, courses: dict) -> set:
    con = sqlite3.connect(database)
    courses_rows = pd.read_sql_query(
        """select * FROM predmet
        where predmet.idpred in
        (SELECT export.idpred
        FROM export
        GROUP BY export.idpred
        HAVING COUNT(export.idpred) = 1)""", con)
    only_one_enrollment_courses = set()
    for index, row in courses_rows.iterrows():
        only_one_enrollment_courses.add(courses[int(row['idpred'])])
    con.close()
    return only_one_enrollment_courses


def get_doctoral_courses(database: str, courses: dict) -> set:
    con = sqlite3.connect(database)
    doctoral_rows = pd.read_sql_query(
        """SELECT *
        FROM predmet""", con)
    doctoral_courses = set()
    for index, row in doctoral_rows.iterrows():
        course = row['skratkapred']
        if course.startswith('3-'):
            doctoral_courses.add(courses[int(row['idpred'])])
    con.close()
    return doctoral_courses


def get_number_of_students_and_courses_per_years(database):
    con = sqlite3.connect(database)
    entriees = pd.read_sql_query("SELECT id, akrok, idpred FROM export", con)
    students_per_year = {}
    courses_per_year = {}
    for index, row in entriees.iterrows():
        if row['akrok'] not in courses_per_year.keys():
            courses_per_year[row['akrok']] = [row['idpred']]
        else:
            if row['idpred'] not in courses_per_year[row['akrok']]:
                courses_per_year[row['akrok']].append(row['idpred'])

        if row['akrok'] not in students_per_year.keys():
            students_per_year[row['akrok']] = [row['id']]
        else:
            if row['id'] not in students_per_year[row['akrok']]:
                students_per_year[row['akrok']].append(row['id'])
    return students_per_year, courses_per_year


def teachers(all_data):
    bachelors = 0
    masters = 0
    for entry in all_data:
        if entry[3].startswith('up'):
            bachelors += 1
        if entry[3].startswith('mu'):
            masters += 1
    return bachelors, masters



class Evaluator:
    def __init__(self, number_of_courses, RMSE_courses, fields_division, test_data):
        self.number_of_courses = number_of_courses
        self.RMSE_courses = RMSE_courses
        self.fields_division = fields_division
        self.test_data = test_data

    def evaluate(self, trained_model):
        RMSEs = []
        fields_RMSEs = []
        for i in range(0, 8):
            fields_RMSEs.append([])
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
            RMSE /= self.RMSE_courses
            RMSE = np.sqrt(RMSE)
            RMSEs.append(RMSE)
            fields_RMSEs[self.fields_division[data[3]] - 1].append(RMSE)
        total_score = np.sum(RMSEs)
        total_score /= len(self.test_data)
        score_per_field = {
            'MAT_b': 0, 'INF_b': 0, 'FYZ_b': 0, 'UCITELSTVO_b': 0, 'MAT_m': 0, 'INF_m': 0, 'FYZ_m': 0, 'UCITELSTVO_m': 0
        }
        keys = [k for k, v in score_per_field.items()]
        for i in range(len(fields_RMSEs)):
            if len(fields_RMSEs[i]) == 0:
                score_per_field[keys[i]] = None
                continue
            score = np.sum(fields_RMSEs[i])
            score /= len(fields_RMSEs[i])
            score_per_field[keys[i]] = score
        return total_score, score_per_field


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
