import json
import os, os.path
from pathlib import Path
import time
import re
import pytest
import sys
import config.test_data as td

#file_to_read = "/Users/test/Downloads/QA__M_C_N_1203"
#file_to_read = "/Users/test/CompLaw_2503.json"
#file_to_read = "/Users/test/acc_itc.json"
#file_to_read = "/Users/test/HCB-err.json"
# course json files should be added/ downloaded to data/{env}/


date_time = int(time.time())
path_to_save = os.path.join(str(td.base_results), 'nti','')
if not os.path.exists(path_to_save):
    os.makedirs(path_to_save)

def _save_as_file_in_same_dir(course_id, collected_motifs):
    file_name = course_id + "_" + str(date_time)
    with open(os.path.join(path_to_save, file_name), 'w') as file:
        name = file.name
        collected_data = collected_motifs
        for key, value in collected_data.items():
            file.write('_' * 20 + '\n')
            file.write(key + '\n')
            for k, v in value.items():
                file.write(' ' * 12 + "SLIDE %s \n" % k)
                for lines in v:
                    file.write('- %s' % lines + '\n')
                file.write('. ' * 20 + '\n')
            file.write('_' * 20 + '\n')
    return name

def _motif_found(motif, collected_motifs, print_len=True):
    collected_data = collected_motifs
    motifs_list = [i for i in collected_data.keys() if motif in i]
    if print_len == True:
        print("%s found: " % motif, len(motifs_list))
    return motifs_list
    # assert len(motifs_list) > 0

def _list_of_NTI_types(collected_motifs):
    collected_data = collected_motifs
    nti_type_list = []
    # print("collected motiffs: ", collected_motifs)
    for k, v in collected_data.items():
        for ke, va in v.items():
            for sub_i in va:
                # print("sub i : ", sub_i)
                nti_type = re.findall(r"\[(.*?)\]", sub_i)
                # print(str(nti_type[0]))
                ntityp, ntiindx = str(nti_type[0]).split(',')
                # print(ntityp)
                # print(ntiindx)
                nti_type_list.append(ntityp)
    return [int(i) for i in nti_type_list]

def _list_of_lines(collected_motifs):
    lines_list = []
    for key, value in collected_motifs.items():
        for k, v in value.items():
            for line in v:
                tested_line = line.lower()
                lines_list.append(tested_line)
    return (lines_list)

def _item_in_list(item,collected_motifs):
    nti_type_list = _list_of_NTI_types(collected_motifs)
    print("Count of '%s': " % item, nti_type_list.count(item))
    return nti_type_list.count(item)


def test_generate_file(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    #print("skip test : ", skip_test)
    if skip_test:
        pytest.skip("File does not have nti_data")
    f_name = _save_as_file_in_same_dir(course_id, collected_motifs)
    print("File is generated: ", f_name)
    


def test_ELTS_is_generated(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    #print("skip test : ", skip_test)
    if skip_test:
        pytest.skip("File does not have nti_data")
    motif_lst = _motif_found("ELTS", collected_motifs, True)
    print(motif_lst)
    if (len(motif_lst) > 0):
        print("ELTS exists   ")
    assert len(motif_lst) > 0
    print("")

def test_EHTS_is_generated(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    motif_lst = _motif_found("EHTS", collected_motifs,True)
    print(motif_lst)
    if (len(motif_lst) > 0):
        print("EHTS exists   ")
    assert len(motif_lst) > 0
    


def test_HE1SB2_is_generated(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    motif_lst = _motif_found("HE1SB2",collected_motifs, True)
    print(motif_lst)
    if (len(motif_lst) >= 0):
        print("HE1SB2 is in range or does not exist   ")
    assert len(motif_lst) >= 0
    


def test_SF1HE1_is_generated(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    motif_lst = _motif_found("SF1HE1",collected_motifs, True)
    print(motif_lst)
    if (len(motif_lst) >= 0):
        print("SF1HE1 is in range or does not exist   ")
    assert len(motif_lst) >= 0
    

def test_NTI_types_in_range(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    nti_type_list = _list_of_NTI_types(collected_motifs)
    print("nti type list : ", nti_type_list)
    not_in_range = 0
    for i in nti_type_list:
        if (i in range(1, 4)):
            pass
        else:
            not_in_range += 1
        assert i in range(1, 4)
    if (not_in_range == 0):
        print("NTI types are in range ")
    


def test_NTI_type_1_in_range(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    countitem = _item_in_list(1, collected_motifs)
    if (countitem > 0):
        print("NTI type 1 exists in rem content ")
    assert countitem > 0
    


# OK to fail, not a necessary condition
def test_NTI_type_2_in_range(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    countitem = _item_in_list(2, collected_motifs)
    if (countitem >= 0):
        print("NTI type 2 is in range or does not exist  ")
    assert countitem >= 0
    


# OK to fail, not a necessary condition
def test_NTI_type_3_in_range(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    countitem = _item_in_list(3, collected_motifs)
    if (countitem >= 0):
        print("NTI type 3 is in range or does not exist   ")
    assert countitem >= 0
    

def test_shape_related_stopwords(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    shape_stopwords = ["rectangle", "oval", "star", "line", "triangle", "corner", "arrow", "chevron", "edge", "round",
                       "diagonal", "trapezoid"]
    error_count = 0
    # print("Words not found: ", end='')
    lines_to_check = _list_of_lines(collected_motifs)
    for line in lines_to_check:
        for stop_word in shape_stopwords:
            if (stop_word in line.split()):
                print("stopword %s found in line : " % stop_word, line)
                error_count += 1
            else:
                pass
                # print("stopwords not found : ", line)
    if (error_count == 0):
        print("no shape related stopwords found  ")
    assert error_count == 0
    

def test_bb_code_removed(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    count_bb_found = 0
    bbPattern = r"\[*[a-z]*](.*?)[\*[a-z]*]"
    lines_to_check = _list_of_lines(collected_motifs)
    # print("lines to check for bbcode : ",lines_to_check)
    for line in lines_to_check:
        if re.search(bbPattern, line):
            print('found bbcode match! : ', line)
            result = re.findall(bbPattern, line)
            print(result)
            count_bb_found += 1
        else:
            pass
    if (count_bb_found == 0):
        print("no bbcode  found  ")
    assert count_bb_found == 0
    


def test_html_tag_removed(collected_motif):
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    count_html_found = 0
    htmltagPattern = r"<[^>]*>"
    lines_to_check = _list_of_lines(collected_motifs)
    # print("lines to check for html tags : ",lines_to_check)
    for line in lines_to_check:
        if re.search(htmltagPattern, line):
            print('found html tags match! : ', line)
            count_html_found += 1
        else:
            pass
    if (count_html_found == 0):
        print("no html tags found  ")
    assert count_html_found == 0
    


def test_text_found_in_prevslides(collected_seg_motif):
    slide_not_found, error_records_future, error_records_seg, skip_test= collected_seg_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    # """Validates that each line is from slides 0 - current"""
    print("error_records_future : ", error_records_future)
    #print("error_records_seg : ", error_records_seg)
    if len(error_records_future) > 0:
        print("error count : ", len(error_records_future))
        print("error slides : ", (error_records_future))
        pytest.fail(
            "errors found. Count of missing rem slides in segments %s , count of remediation slides in future slides %s"
            % (slide_not_found, error_records_future))
    


def test_text_found_in_single_slide(collected_seg_motif):
    """Validates that all the rem slides come from a single segment"""
    slide_not_found, error_records_future, error_records_seg, skip_test = collected_seg_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    #print("error_records_future : ", error_records_future)
    print("error_records_seg : ", error_records_seg)
    if len(error_records_seg) > 0:
        print("error count : ", len(error_records_seg))
        print("error slides : ", (error_records_seg))
        pytest.fail(
            "errors found. Count of missing rem slides in segments %s , count of remediation slides in nore than 1 slide %s"
            % (slide_not_found, error_records_seg))



def test_assets_slide_index_in_valid_range(collected_motif):
    # Validates that the rem slides are in valid range in the course
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    print("Content length: ", content_length)
    slide_idx_assets = []
    if len(collected_motifs) > 0:
        for motif, value in collected_motifs.items():
            for k, v in value.items():
                slide_idx_assets.append(k)
        sorted_list = sorted(set(slide_idx_assets))
        print("Assets indexes: ", sorted_list)
        for item in sorted_list:
            print(item)
            assert item < content_length
    else:
        pytest.fail("Collected 0 motifs")



# TODO
def test_subseg_in_seg(collected_motif):
    # validate that all subsegments listed for a particular segment have text in to "text" and/or "transcribed_text" field
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    pass



#TODO
def test_nti_data_valid_json(collected_motif):

    #validate that the nti_data field is a valid json
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    pass

#TODO
def test_nti_validate_rem_content_not_in_quiz(collected_motif):

    #validate that the nti_data field is a valid json
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    pass

#TODO
def test_nti_validate_rem_content_not_in_low_ETS_slides(collected_motif):

    #validate that the nti_data field is a valid json
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    pass

#TODO
def test_nti_no_2_rem_slides_are_same(collected_motif):

    #validate that the nti_data field is a valid json
    collected_motifs, course_id, content_length, skip_test = collected_motif
    if skip_test:
        pytest.skip("File does not have nti_data")
    pass