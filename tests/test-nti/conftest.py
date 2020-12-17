import json
import pathlib
import time
import os

import pytest
import sys
import config.test_data as td
#import get_data.post


sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))



def pytest_addoption(parser):
    parser.addoption('--nti_json_file', action="store", default="", help='nti_json_file should be added to data/{env}/ folder or full path provided  --nti_json_file=HCP-err.json ')

def pytest_configure(config):
    print("start testing")
    nti_json_file = config.option.nti_json_file
    print('file to test : ' , nti_json_file)
    if "/" in str(nti_json_file):
        filenm =   nti_json_file
        print("filename : ", filenm)
    else :
        print("in else")
        filenm = td.base_data + nti_json_file
        print("filename : ",filenm)
    config.cache.set("nti_json_file", filenm)

@pytest.fixture(scope="module")
def collected_motif(request):
    print("start testing- collected motif")
    crs_file = request.config.cache.get("nti_json_file", None)
    print(crs_file)
    print('file to test : ',request.config.cache.get("nti_json_file", None))
    collected_motifs, course_id, content_length, skip_test = _read_file(crs_file)
    request.config.cache.set("skip_test", skip_test)
    return (collected_motifs, course_id, content_length, skip_test)

@pytest.fixture(scope="module")
def collected_seg_motif(request):
    print("start testing - collected seg motif")
    crs_file = request.config.cache.get("nti_json_file", None)
    print(crs_file)
    print('file to test : ',request.config.cache.get("nti_json_file", None))
    skip_test = request.config.cache.get("skip_test", None)
    collected_seg_subseg = _collect_seg_subseg(crs_file, skip_test)
    collected_motif_slides = _collect_motif_slides(crs_file, skip_test)
    #print("collected seg : ", collected_seg)
    #print("collected value motif : ", collected_value_motif)
    slide_not_found, error_records_future, error_records_seg = _compare_seg_motif(collected_seg_subseg, collected_motif_slides, skip_test)
    return (slide_not_found,error_records_future ,error_records_seg, skip_test)




def _read_file(course_filename):
    # open the file and find all motifs
    print("read file")
    numeric_id = 0
    course_id=''
    content_length = 0
    skip_test = False
    nti_data_motif = {}
    with open(course_filename, 'r') as f:
        filedata = f.read()
        json_filedata = json.loads(filedata)
    try :
        nti_data_motif = json_filedata['modules'][0]['units'][0]['contents'][0]['nti_data']
    except Exception:
        skip_test = True
        print("Unexpected error, nti_data probably does not exist:", sys.exc_info()[0])
        pass
        #raise
    collected_motifs = {}
    # in each motif save as dict[type of motif] = dict[slide_id] = list of lines
    for i in nti_data_motif:
        #key_item_name = str(i['properties_json']['motifType']) + '_' + str(i['numeric_id'])
        key_item_name = str(i['properties_json']['motifType']) + '_' + str(i['properties_json']['altContIdx'])
        value_motif = {}
        for idx, altContIdx_item in enumerate(i['properties_json']['alternateContent']):
            value_motif_part = []
            alt_cont_ind = int(i['properties_json']['altContIdx'][idx])
            for n in altContIdx_item:
                segment_type = n['segment_type']
                segment_index = n['segment_index']
                value_motif_part.append("[%s , %s] " % (segment_type,segment_index) + ' * '.join(n['content']))
            value_motif[alt_cont_ind] = value_motif_part
        collected_motifs[key_item_name] = value_motif
        course_id = json_filedata['id']
    # course length
    #print("skip test : ", skip_test)
    if not skip_test :
        content_length = json_filedata['modules'][0]['units'][0]['contents'][0]['length']

    return (collected_motifs, course_id, content_length, skip_test)


def _collect_seg_subseg(course_filename, skip_test):
    # open the file and find all segments and subsegments
    numeric_id = 0
    course_id=''
    seg_subseg = {}
    with open(course_filename, 'r') as f:
        filedata = f.read()
        json_filedata = json.loads(filedata)
    if not skip_test:
        seg_subseg = json_filedata['modules'][0]['units'][0]['contents'][0]['segments']
    collected_seg_subseg = {}
    # in each motif save as dict[type of motif] = dict[slide_id] = list of lines
    for i in seg_subseg:
        #key_item_name = str(i['properties_json']['motifType']) + '_' + str(i['numeric_id'])
        key_seg = str(i['index'])
        value_sub_seg = []
        for subseg in (i['subsegments']):
            segment_type = str(subseg['segment_type'])
            segment_index = subseg['segment_index']
            value_sub_seg.append("[%s , %s] " % (segment_type,segment_index))
        #value_motif[alt_cont_ind] = value_sub_seg
        collected_seg_subseg[key_seg] = value_sub_seg
    return (collected_seg_subseg)



def _collect_motif_slides(course_filename, skip_test):
    # open the file and find all motifs
    file_to_read = course_filename
    numeric_id = 0
    course_id = ''
    nti_data_motif = {}
    with open(file_to_read, 'r') as f:
        filedata = f.read()
        json_filedata = json.loads(filedata)
    if not skip_test:
        nti_data_motif = json_filedata['modules'][0]['units'][0]['contents'][0]['nti_data']

    collected_motif_slides = {}
    collected_value_motif = {}
    # in each motif save as dict[type of motif] = dict[slide_id] = list of lines
    for i in nti_data_motif:
        # key_item_name = str(i['properties_json']['motifType']) + '_' + str(i['numeric_id'])
        key_item_name = str(i['properties_json']['motifType']) + '_' + str(i['properties_json']['altContIdx'])

        for idx, altContIdx_item in enumerate(i['properties_json']['alternateContent']):
            value_motif_part = []
            alt_cont_ind = str(i['properties_json']['altContIdx'][idx]) + '-' + str(i['properties_json']['motifType'])
            for n in altContIdx_item:
                segment_type = n['segment_type']
                segment_index = n['segment_index']
                value_motif_part.append("[%s , %s] " % (segment_type, segment_index))
            collected_value_motif[alt_cont_ind] = value_motif_part
            collected_motif_slides[key_item_name] = collected_value_motif

    return (collected_value_motif)


def _compare_seg_motif(collected_seg_subseg, collected_motif_slides, skip_test):
    #compare segments, subsegments and motiffs
    if skip_test:
        pytest.skip("File does not have nti_data")
    # """Validates that each line is from slides 0 - current"""
    #print("collected_seg : ", collected_seg_subseg)
    #print("collected motiffs : ", collected_motif_slides)
    value_motif = []
    error_prev_slide = 0
    slide_not_found = 0
    error_records_future = []
    error_records_seg = []
    for motif, slides in collected_motif_slides.items():
        print(motif, slides)
        slideid, motiftyp = str(motif).split('-')
        print(slideid)
        print(motiftyp)
        seg = []
        # skip forward can take text from the slides skipped in forward direction which is 2 at max
        value_motif = slides
        for a in value_motif:
            #print("motiff type, seg index : ", a)
            for b, c in collected_seg_subseg.items():
                # print(  b, c)
                if a in c:
                    print("motif exists in segment : ", b)
                    seg.append(b)
            if len(seg) <= 0:
                print("motiff was not found in any segments ")
                slide_not_found += 1
                error_prev_slide += 1
                error_records_future.append(
                    'remSlide-' + str(slideid) + ',' + motiftyp + ',' + str(a) + 'found in segIndex-' + str(
                        seg))
                error_records_seg.append(
                    'remSlide-' + str(slideid) + ',' + motiftyp + ',' + str(a) + 'found in segIndex-' + str(
                        seg))
            else:
                print("segment list : ", len(seg))
                # insert the list to the set
                list_set = set(seg)
                # convert the set to the list
                unique_list = (list(list_set))
                print("number of unique segments : ", len(unique_list))
                print("unique seg indexs : ", unique_list)
                if len(unique_list) > 1:
                    error_records_seg.append(
                        'remSlide-' + slideid + ',' + motiftyp + ',' + a + 'found in segIndex-' + str(unique_list))
                for s in unique_list:
                    # print(s)
                    if motiftyp == 'SF1HE1':
                        newval = int(slideid) + 5
                        if (int(s) < newval):
                            pass
                        else:
                            print(" remediation slide is from from future slides")
                            error_prev_slide += 1
                            error_records_future.append(
                                'remSlide-' + str(slideid) + ',' + motiftyp + ',' + str(a) + 'found in segIndex-' + str(
                                    s))

                    elif int(s) < int(slideid):
                        # print("slide id : ", slideid)
                        pass
                    else:
                        print(" remediation slide is from from future slides")
                        error_prev_slide += 1
                        error_records_future.append(
                            'remSlide-' + str(slideid) + ',' + motiftyp + ',' + str(a) + 'found in segIndex-' + str(s))
        print(50 * '*')
    return(slide_not_found,error_records_future ,error_records_seg)
