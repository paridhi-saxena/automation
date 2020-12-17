import pathlib
import time
import os
from src.get_data.get_cta_from_s3 import *
import sys
import config.test_data as td
#import get_data.post


sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

global files

def pytest_addoption(parser):
    parser.addoption('--legacy', action="store_false", default=False, help='are these legacy ctas? True/False ')
    parser.addoption('--cta_courseids', action="append", default=[], help='course ids for cta --cta_courseids=course123 --cta_courseids=course123 ')
    parser.addoption('--ctlid', action="store", default='acc', help='three letter company id for v2 --ctlid=moo')



def pytest_configure(config):
    print("start testing")
    crsids = config.option.cta_courseids
    legacy = config.option.legacy
    ctlid = config.option.ctlid
    get_folder_list(legacy, ctlid, crsids)
        #return files

'''@pytest.fixture(scope='session')
def filename2(request):
    name_value = request.config.option.cta_courseids
    files = []
    if request.param == "d1":
        if name_value is None:
            pytest.skip()
        else :
            files = get_folder_list()
    print('cta course ids : ', name_value)
    return files'''



def pytest_generate_tests(metafunc):
    if 'cta_data' in metafunc.fixturenames:
        print("cta_data")
        coral_heatmaps = 'coral-heatmaps'
        legacy_heatmaps = 'heatmaps-by-company-id'
        download_legacy = metafunc.config.getoption('legacy')
        if download_legacy:
            heatmaps = legacy_heatmaps
        else:
            heatmaps = coral_heatmaps
        companyid = '/' + metafunc.config.getoption('ctlid')
        download_to_folder = td.base_data_set+'/'+ heatmaps+companyid
        files_list = []
        for filepath in pathlib.Path(download_to_folder).glob('**/*'):
            print(filepath.absolute())
            if ('stemmed_topic_word_mapping.csv' in str(filepath.absolute())):
                files_list.append(str(filepath.absolute()))
        print(" ")
        print("file list in conftest: ", files_list)
        metafunc.parametrize("cta_data", files_list)



#@pytest.mark.usefixtures("cta_courseids")
def get_folder_list(legacy=False, ctlid = "", crsid = []):
    env = td.env
    print(env)
    #print('cta course ids : ', cta_courseids)
    profile_name = td.profile_name
    bucketname_cta = os.getenv('CTA_BUCKET', 'test-%s-dashboard' % env)
    coral_heatmaps = 'coral-heatmaps'
    legacy_heatmaps = 'heatmaps-by-company-id'
    download_legacy = legacy
    bktname_junk = td.bucketname_junkdrawer
    s3_folder_junk = 'cta/cta_stoplist.txt'
    if legacy :
        heatmaps = legacy_heatmaps
    else :
        heatmaps = coral_heatmaps
    companytlid = ctlid
    # companytlid = 'f8753e8e-7dcc-49e1-ba4b-a746589f233d'

    download_to_folder = td.base_data_set
    companyid = '/' + companytlid
    # if you want to test just a particular course add the courseid as /courseid
    # example : https://s3.amazonaws.com/test-proto-dashboard/coral-heatmaps/abc/OLP3-QA
    # example: https://s3.amazonaws.com/test-proto-dashboard/heatmaps-by-company-id/f8753e8e-7dcc-49e1/FAIRY_TEST
    # courseids = ['OLP3-QA', 'ACHI']
    courseids = crsid
    print(courseids)
    print(len(courseids))
    if len(courseids) == 0:
        if download_legacy:
            s3_folder = legacy_heatmaps + companyid
        else:
            s3_folder = coral_heatmaps + companyid
        get_cta = cta_assets()
        get_cta.download_cta_from_s3(env, s3_folder, download_to_folder, bucketname_cta, profile_name)
        get_cta.download_ctastopwords_from_s3(env, s3_folder_junk, download_to_folder, bktname_junk, profile_name)
    else:
        for crs in courseids:
            #print(" in for : ")
            courseid = '/' + crs
            if download_legacy:
                s3_folder = legacy_heatmaps + companyid + courseid
            else:
                s3_folder = coral_heatmaps + companyid + courseid

            get_cta = cta_assets()
            get_cta.download_cta_from_s3(env, s3_folder, download_to_folder, bucketname_cta, profile_name)
            get_cta.download_ctastopwords_from_s3(env, s3_folder_junk, download_to_folder, bktname_junk, profile_name)



