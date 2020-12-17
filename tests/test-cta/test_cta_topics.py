import pathlib
import unittest
import trace, sys
import datetime

import os
import pytest

from src.validate_functions.cta_file_compare import *
from src.common.util.json_to_csv import *
from src.get_data.get_cta_from_s3 import *
import config.test_data as td

sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))


def test_1_compare_single_column(cta_data):
    print('cta data : ', cta_data)
    duplicates_found = pandas_compare_single_column(cta_data)
    if (duplicates_found == 0):
        assert True
        print("single columns do not contain duplicates")
    else:
        # assertEqual( 0,missing_recs, "Usercourse.csv is missing data")
        print("total duplicates found : ", duplicates_found)
        pytest.fail("duplicates values in single columns found")


def test_2_compare_rows(cta_data):
    print(cta_data)
    duplicate_rows = pandas_compare_rows(cta_data)

    if (duplicate_rows == 0):
        assert True
        print("no duplicate rows found")

    else:
        pytest.fail("duplicate for rows found")
        print("duplicate rows found : ", duplicate_rows)


def test_3_compare_columns(cta_data):
    print(cta_data)
    duplicates_found = pandas_compare_columns(cta_data)
    if (duplicates_found == 0):
        assert True
        print("no duplicate columns found")
    else:
        pytest.fail("duplicate for columns found")
        print("number of duplicate columns found : ", duplicates_found)


def test_4_compare_against_stopwords(cta_data):
    print(cta_data)
    download_to_folder = td.base_data_set
    stopwords = download_to_folder + 'cta/cta_stoplist.txt'
    duplicates_found = pandas_compare_stopwords(cta_data, stopwords)
    if (duplicates_found == 0):
        assert True
        print("no stopwords found")
    else:
        pytest.fail("stopwords found in the list")
        print("number of stopwords found : ", duplicates_found)


if __name__ == "__main__":
    t = trace.Trace(ignoredirs=[sys.prefix, sys.exec_prefix], count=1, trace=0)
    t.runfunc(unittest.main)
    r = t.results()
    r.write_results(show_missing=True)
    print("starting pre tasks")
    # start_pre_tasks()
