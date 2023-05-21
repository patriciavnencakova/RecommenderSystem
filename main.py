import sqlite3

import sys as s
from typing import Tuple
import numpy as np
import pandas as pd


def main():
    study_programmes, fields_division = get_programs("ais2022.db")

    courses, courses_names = get_courses("ais2022.db")
    same_courses = merge_same_courses("ais2022.db", courses)

    doctoral_courses = get_doctoral_courses("ais2022.db", courses)
    no_enrollment_courses = get_courses_with_no_enrollment("ais2022.db", courses)
    only_one_enrollment_courses = get_courses_with_only_one_enrollment("ais2022.db", courses)
    redundant_courses = doctoral_courses.union(only_one_enrollment_courses).union(no_enrollment_courses)
    RMSE_courses = len(same_courses) - len(redundant_courses)

    all_data = load_all_data("ais2022.db", courses)

    train_years = ["2015/16", "2016/17", "2017/18", "2018/19", "2019/20"]
    test_years = ["2020/21", "2021/22"]
    train_data, test_data = separate_data_into_test_and_train("ais2022.db", all_data, train_years, test_years)

    jaccard_index_rs = JaccardIndexRS(courses, redundant_courses, 15)
    jaccard_index_rs.train(train_data)
    my_data = [
        [1783, 1569, 1873, 4259, 1931, 174, 1733, 1526, 3485, 3447, 1302, 1871, 1874, 8, 4411, 182, 1734, 1533],
        [],
        "2021/22",
        "INF",
    ]
    prediction = jaccard_index_rs.predict(my_data)
    for i in range(len(prediction)):
        if prediction[i] != 0:
            print(f"{i}: {prediction[i]}")

    evaluator = Evaluator(len(courses), RMSE_courses, fields_division, test_data)
    (
        total_score_RMSE,
        score_per_field_RMSE,
        total_score_F1,
        score_per_field_F1,
    ) = evaluator.evaluate(jaccard_index_rs)
    print("total computed RMSE value: ", total_score_RMSE)
    print(score_per_field_RMSE)
    print("total computed F1-score value: ", total_score_F1)
    print(score_per_field_F1)


def load_all_data(database: str, courses: dict) -> list:
    con = sqlite3.connect(database)
    students_rows = pd.read_sql_query("SELECT DISTINCT id FROM export", con)
    students_rows.reset_index()
    students = []
    for index, row in students_rows.iterrows():
        students.append(int(row["id"]))

    all_data = []

    for student in students:
        years_per_student_rows = pd.read_sql_query(
            f"SELECT DISTINCT akrok "
            f"FROM export "
            f"WHERE id = {student} "
            f"ORDER BY akrok",
            con,
        )
        years_per_student_rows.reset_index()
        years_per_student = []
        for index, row in years_per_student_rows.iterrows():
            years_per_student.append(row["akrok"])

        courses_so_far = []
        for year in years_per_student:
            all_data_item = []
            y_courses_rows = pd.read_sql_query(
                f"SELECT idpred, skratkasp"
                f" FROM export"
                f" WHERE id = {student} AND akrok = '{year}'",
                con,
            )
            courses_this_year = []
            program = str()
            for index, row in y_courses_rows.iterrows():
                courses_this_year.append(courses[int(row["idpred"])])
                program = row["skratkasp"]
            all_data_item.extend(
                [courses_so_far.copy(), courses_this_year, year, program]
            )
            all_data.append(all_data_item)
            courses_so_far.extend(courses_this_year)
    con.close()
    return all_data


def separate_data_into_test_and_train(
    database: str, all_data: list, train_years: list, test_years: list
) -> Tuple[list, list]:
    con = sqlite3.connect(database)
    years_rows = pd.read_sql_query(
        "SELECT DISTINCT akrok FROM export ORDER BY akrok DESC", con
    )
    years_rows.reset_index()
    years = []
    for index, row in years_rows.iterrows():
        years.append(row["akrok"])
    train_data = []
    test_data = []
    for entry in all_data:
        if entry[2] in test_years:
            test_data.append(entry)
        if entry[2] in train_years:
            train_data.append(entry)
    return train_data, test_data


def get_courses(database: str) -> Tuple[dict, dict]:
    con = sqlite3.connect(database)
    courses_rows = pd.read_sql_query(
        """SELECT DISTINCT idpred, nazovpred, skratkapred
        FROM predmet
        ORDER BY idpred""",
        con,
    )

    courses = {}
    courses_names = {}
    counter = 0
    for index, row in courses_rows.iterrows():
        idpred = int(row["idpred"])
        if idpred in courses.keys():
            continue
        courses[idpred] = counter
        courses_names[idpred] = row["nazovpred"]
        counter += 1
    con.close()
    return courses, courses_names


def get_programs(database: str) -> Tuple[dict, dict]:
    con = sqlite3.connect(database)
    programs_rows = pd.read_sql_query("SELECT DISTINCT skratkasp " "FROM export ", con)
    programs = {}
    for index, row in programs_rows.iterrows():
        programs[row["skratkasp"]] = index
    con.close()
    # 1 = MAT-b, 2 = CS-b, 3 = PHY-b, 4 = TEA-b, 5 = MAT-m, 6 = CS-m, 7 = PHY-m, 8 = TEA-m
    fields_division = {'MAT': 1, 'PMA': 1, 'INF': 2, 'mMMN': 5, 'MMN': 1, 'AIN': 2, 'mFFP': 7, 'FYZ': 3, 'muMAFY': 8,
                       'BMF': 3, 'mAIN': 6, 'mMAT': 5, 'mEOM': 7, 'OZE': 3, 'mINF': 6, 'EFM': 1, 'mFBM': 7, 'muMAIN': 8,
                       'upMAIN': 4, 'mFBF': 7, 'upMAFY': 4, 'mIKV': 6, 'mEMM': 5, 'upINAN': 4, 'mPMS': 5, 'mFTF': 7,
                       'mEFM': 5, 'mFTL': 7, 'mMPG': 5, 'mFFZ': 7, 'BIN': 2, 'mAIN/k': 6, 'DAV': 2, 'muMAFY/k': 8,
                       'mFJF': 7, 'muMADG': 8, 'upMADG': 4, 'mIKVa': 6, 'muMATV': 8, 'upMATV': 4, 'mINF/k': 6,
                       'mFAA': 7, 'muMAIN/k': 8, 'FYZ/k': 3, 'mAINa': 6, 'mFOS': 7, 'mFPE': 7, 'mFMK': 7, 'mINFa': 6,
                       'mFOZ': 7, 'muMADG/k': 8, 'TEF': 3, 'DAV/k': 2, 'mFTFa': 7, 'muFYIN': 8, 'upFYIN': 4,
                       'upINBI': 4, 'mMATa': 5, 'AINa': 2, 'BIN/k': 2, 'mINFa/k': 6, 'OZE/k': 3, 'mMPGa': 5, 'mEOMa': 7,
                       'TEF/k': 3, 'mFJFa': 7, 'muINBI': 8, 'FYZa': 3}
    return programs, fields_division


def merge_same_courses(database: str, courses: dict) -> dict:
    con = sqlite3.connect(database)
    courses_rows = pd.read_sql_query("SELECT * FROM predmet", con)
    duplicate_courses = {}
    for index, row in courses_rows.iterrows():
        key = f"{row['skratkapred']}_{row['nazovpred']}"
        parts = row["kodpred"].split("/")
        idpred = int(row["idpred"])
        if key in duplicate_courses:
            value = duplicate_courses[key]
            if value["max_value"] < int(parts[-1]):
                value["max_value"] = int(parts[-1])
                value["max_id"] = courses[idpred]
            value["courses"].append(idpred)
        else:
            value = {
                "max_value": int(parts[-1]),
                "max_id": courses[idpred],
                "courses": [idpred],
            }
            duplicate_courses[key] = value

    for key, value in duplicate_courses.items():
        for course in value["courses"]:
            courses[course] = value["max_id"]
    con.close()
    return duplicate_courses


def get_courses_with_only_one_enrollment(database: str, courses: dict) -> set:
    con = sqlite3.connect(database)
    courses_rows = pd.read_sql_query(
        """SELECT * FROM predmet
        WHERE predmet.idpred IN
        (SELECT export.idpred
        FROM export
        GROUP BY export.idpred
        HAVING COUNT(export.idpred) = 1)""",
        con,
    )
    only_one_enrollment_courses = set()
    for index, row in courses_rows.iterrows():
        only_one_enrollment_courses.add(courses[int(row["idpred"])])
    con.close()
    return only_one_enrollment_courses


def get_courses_with_no_enrollment(database: str, courses: dict) -> set:
    con = sqlite3.connect(database)
    courses_rows = pd.read_sql_query(
        """SELECT * FROM predmet
        where predmet.idpred NOT IN
        (SELECT export.idpred
        FROM export);""",
        con,
    )
    no_enrollment_courses = set()
    for index, row in courses_rows.iterrows():
        no_enrollment_courses.add(courses[int(row["idpred"])])
    con.close()
    return no_enrollment_courses


def get_doctoral_courses(database: str, courses: dict) -> set:
    con = sqlite3.connect(database)
    doctoral_rows = pd.read_sql_query(
        """SELECT * FROM predmet""",
        con,
    )
    doctoral_courses = set()
    for index, row in doctoral_rows.iterrows():
        course = row["skratkapred"]
        if course.startswith("3-"):
            doctoral_courses.add(courses[int(row["idpred"])])
    con.close()
    return doctoral_courses


class Evaluator:
    def __init__(self, number_of_courses, RMSE_courses, fields_division, test_data):
        self.number_of_courses = number_of_courses
        self.RMSE_courses = RMSE_courses
        self.fields_division = fields_division
        self.test_data = test_data

    def evaluate(self, trained_model):
        RMSEs = []
        fields_RMSEs = []
        F1s = []
        fields_F1s = []
        for i in range(0, 8):
            fields_RMSEs.append([])
            fields_F1s.append([])
        for data in self.test_data:
            reality = data[1]
            prediction = trained_model.predict(data)
            RMSE = 0
            TP = 0
            FN = 0
            FP = 0
            for i in range(self.number_of_courses):
                if i in reality:
                    RMSE += np.power(prediction[i] - 1, 2)
                else:
                    RMSE += np.power(prediction[i], 2)
                if i in reality and prediction[i] >= 0.3:
                    TP += 1
                elif i in reality and prediction[i] < 0.3:
                    FN += 1
                elif i not in reality and prediction[i] >= 0.3:
                    FP += 1
            RMSE /= self.RMSE_courses
            RMSE = np.sqrt(RMSE)
            RMSEs.append(RMSE)
            fields_RMSEs[self.fields_division[data[3]] - 1].append(RMSE)

            if TP == 0:
                F1s.append(0)
                fields_F1s[self.fields_division[data[3]] - 1].append(0)
                continue
            precision = TP / (TP + FP)
            recall = TP / (TP + FN)
            F1 = (2 * precision * recall) / (precision + recall)
            F1s.append(F1)
            fields_F1s[self.fields_division[data[3]] - 1].append(F1)
        total_score_RMSE = np.sum(RMSEs)
        total_score_RMSE /= len(self.test_data)
        total_score_F1 = np.sum(F1s)
        total_score_F1 /= len(self.test_data)
        score_per_field_RMSE = {
            'MAT-b': 0, 'CS-b': 0, 'PHY-b': 0, 'TEA-b': 0, 'MAT-m': 0, 'CS-m': 0, 'PHY-m': 0, 'TEA-m': 0
        }
        score_per_field_F1 = {
            'MAT-b': 0, 'CS-b': 0, 'PHY-b': 0, 'TEA-b': 0, 'MAT-m': 0, 'CS-m': 0, 'PHY-m': 0, 'TEA-m': 0
        }
        keys1 = [k for k, v in score_per_field_RMSE.items()]
        for i in range(len(fields_RMSEs)):
            if len(fields_RMSEs[i]) == 0:
                score_per_field_RMSE[keys1[i]] = None
                continue
            score = np.sum(fields_RMSEs[i])
            score /= len(fields_RMSEs[i])
            score_per_field_RMSE[keys1[i]] = score

        keys2 = [k for k, v in score_per_field_F1.items()]
        for i in range(len(fields_F1s)):
            if len(fields_F1s[i]) == 0:
                score_per_field_F1[keys2[i]] = None
                continue
            score = np.sum(fields_F1s[i])
            score /= len(fields_F1s[i])
            score_per_field_F1[keys2[i]] = score
        return (
            total_score_RMSE,
            score_per_field_RMSE,
            total_score_F1,
            score_per_field_F1,
        )


class JaccardIndexRS:
    def __init__(self, courses, redundant_courses, n):
        self.data = None
        self.courses = courses
        self.redundant_courses = redundant_courses
        self.n = n

    def train(self, train_data):
        self.data = train_data

    def predict(self, data):
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
            our_tuple = (jaccard_index, dato[1])
            tuples.append(our_tuple)
        tuples.sort(reverse=True)
        top_n = tuples[: self.n]
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
        return result


class HammingDistanceRS:
    def __init__(self, courses, redundant_courses, n):
        self.data = None
        self.courses = courses
        self.redundant_courses = redundant_courses
        self.n = n

    def train(self, train_data):
        self.data = train_data

    def predict(self, data):
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
            our_tuple = (hamming_distance, dato[1])
            tuples.append(our_tuple)
        tuples.sort()
        top_n = tuples[: self.n]
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
        return result


class IntersectionRS:
    def __init__(self, courses, redundant_courses, n):
        self.data = None
        self.courses = courses
        self.redundant_courses = redundant_courses
        self.n = n

    def train(self, train_data):
        self.data = train_data

    def predict(self, data):
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
            our_tuple = (intersection, dato[1])
            tuples.append(our_tuple)
        tuples.sort(reverse=True)
        top_n = tuples[: self.n]
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
        return result


if __name__ == "__main__":
    main()
