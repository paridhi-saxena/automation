import json
import requests
import os
import logging
import boto3 as boto
import test_data
import manta

from manta.util.sessions.CompanySessionManager import CompanySessionManager
from manta.models.platform.course_import.ImportStatus import ImportStatus
from manta.models.platform.course_import.CtaStatus import CtaStatus
from manta.models.backend.user_management.CompanyCourse import CompanyCourse
from manta.models.backend.user_management.Company import Company
from manta.models.backend.course_manager.CTACourse import CTACourse
from manta.util.caches.CompanyCache import CompanyCache

DB_CONFIG = test_data.DB_CONFIG

DB_CONFIG['host'] = os.environ.get('PLATFORM_DB_HOST')
DB_CONFIG['port'] = os.environ.get('PLATFORM_DB_PORT')
DB_CONFIG['user'] = os.environ.get('PLATFORM_DB_USER')
DB_CONFIG['password'] = os.environ.get('PLATFORM_DB_PASS')
DB_CONFIG['db'] = os.environ.get('PLATFORM_DB')

SLACK_USER = os.environ.get('MONITORING_SLACK_USER', 'QA Import Automation Script')
SLACK_WEBHOOK = os.environ.get('MONITORING_SLACK_WEBHOOK',
                                   'https://hooks.slack.com/services/wdjdhjbhbBHBSFDHA/')

manta.initialize(
    platform_db_settings=DB_CONFIG,
    populate_caches=[CompanyCache],
    uwsgi_mode=False
)

sm = CompanySessionManager.get_instance()

headers_all = test_data.headers_all
login_post_payload = test_data.body_post


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
for name in logging.Logger.manager.loggerDict.keys():
    if ('boto' in name) or ('urllib3' in name):
        logging.getLogger(name).setLevel(logging.WARNING)


def _manta_query_companycourse_id(course_id):
    '''
    This method will query company course table to get id as id is required to delete the record via kraken
    Return 0 if no company course row associated with the given course_id
    Return value is important as None will cause _delete_companycourse_id fail.
    :param course_id: string
    :return: id, if record exists else, 0
    '''
    try:
        with sm.get_backend_engine_session() as sesh:
            q = sesh.query(CompanyCourse.id.label('id'))
            q = q.filter(CompanyCourse.course_id == course_id)
            rows = q.all()
            LOGGER.info(rows)
            if len(rows) > 0:
                return rows[0].id
            else:
                return 0
    except Exception as e:
        LOGGER.error('Error in query to Company Course ID: {}'.format(e))
        raise


def _manta_delete_row_courseImport(course_id):
    '''
    This method will first check CTA status table and delete the row if present
    CTA Status row needs to be deleted first as it has FK as course import row
    :param course_id: string id
    '''
    try:
        _manta_delete_row_CTAStatus(course_id)
        with sm.get_platform_engine_session() as sesh:
            q = sesh.query(ImportStatus)
            q = q.filter(ImportStatus.course_id == course_id)
            rows = q.all()
            if len(rows) > 0:
                LOGGER.info('This course has row in course import status table, deleting...')
                q.delete()
                sesh.commit()
            else:
                LOGGER.info("Couldn't find the row for the course id: {}".format(course_id))

    except Exception as e:
        LOGGER.error('Error in deleting the course form Import Status Table: {}'.format(e))
        raise


def _manta_delete_row_CTAStatus(course_id):
    try:
        with sm.get_platform_engine_session() as sesh:
            q = sesh.query(CtaStatus)
            q = q.filter(CtaStatus.course_id == course_id)
            rows = q.all()
            if len(rows) > 0:
                LOGGER.info('This course has CTA Associated to it, deleting...')
                q.delete()
                sesh.commit()
            else:
                LOGGER.info("Couldn't find the row for the course id in CTA Status Table: {}".format(course_id))

    except Exception as e:
        LOGGER.error('Error in deleting the course form CTA Status Table: {}'.format(e))
        raise


def _manta_delete_row_CTACourse(course_id):
    try:
        with sm.get_backend_engine_session() as sesh:
            q = sesh.query(CTACourse)
            q = q.filter(CTACourse.course_id == course_id)
            rows = q.all()
            if len(rows) > 0:
                LOGGER.info('This course has CTA Course row associated to it, deleting...')
                q.delete()
                sesh.commit()
            else:
                LOGGER.info("Couldn't find the row for the course id in CTA Course Table: {}".format(course_id))

    except Exception as e:
        LOGGER.error('Error in deleting the row form CTA Course Table: {}'.format(e))
        raise


def _delete_cta_assets_s3(company_id, course_id, row):
    '''
    This method deletes CTA assets from s3 bucket
    '''
    TLI = _manta_query_company(company_id)
    if TLI is not None:
        success_msg = 'CTA Assets Deletion Completed: '
        failure_msg = 'CTA Assets Deletion Failed: '
        profile_name = test_data.cta_data.get('profile_name')
        bucketname = test_data.cta_data.get('bucketname')
        prefix = 'coral-heatmaps/' + TLI + '/' + course_id
        session = boto.Session()
        profile_list = session.available_profiles
        if len(profile_list) > 0:
            boto_session = boto.Session(profile_name=profile_name)
        else:
            boto_session = boto.Session()
        s3_resource = boto_session.resource('s3')
        bucket = s3_resource.Bucket(bucketname)
        LOGGER.debug(list(bucket.objects.filter(Prefix=prefix)))
        try:
            if len(list(bucket.objects.filter(Prefix=prefix))) > 0:
                bucket.objects.filter(Prefix=prefix).delete()
                LOGGER.info('Deleting CTA Assets...')
                _notify_slack(row, success_msg, failure_msg, success=True)

        except Exception as e:
            LOGGER.error("EXCEPTION IN DELETING CTA FOLDER: {} IN COMPANY: {} is: {}".format(course_id, TLI, e))
            _notify_slack(row, success_msg, failure_msg, success=False)
            raise


def _manta_query_company(company_id):
    try:
        with sm.get_backend_engine_session() as sesh:
            q = sesh.query(Company.three_letter_identifier)
            q = q.filter(Company.id == company_id)
            rows = q.all()
            LOGGER.debug(rows)
            if len(rows) > 0:
                return rows[0].three_letter_identifier
    except Exception as e:
        raise e


def _delete_companycourse_id(companycourse_id):
    '''
    This method deletes company course record using kraken but it will skip if no record is found
    and still return session to the method _delete_user_mgr_course
    Commented out raise exception so that if any error occurs at this method, process still continues.
    '''
    LOGIN_URL = test_data.urls.get('login_url')
    client = requests.session()
    try:
        login_get_response = client.get(LOGIN_URL)
        login_post_payload['csrfmiddlewaretoken'] = login_get_response.cookies['csrftoken']
        client.post(LOGIN_URL, headers=headers_all, data=login_post_payload)

        if companycourse_id != 0:
            companyCourse_delete_url = test_data.urls.get('company_course_url') + str(companycourse_id) + '/delete/'

            companyCourse_get_response = client.get(companyCourse_delete_url)
            companyCourse_payload = {
                'csrfmiddlewaretoken': companyCourse_get_response.cookies['csrftoken'],
                'post': 'yes'
            }
            companycourse_delete_response = client.post(companyCourse_delete_url, headers=headers_all,
                                                      data=companyCourse_payload)
            if companycourse_delete_response.status_code == 200:
                LOGGER.info('Company Course Deleted...')
        return client

    except Exception as e:
        LOGGER.error('Error in deleting the course from Company Course table: {}'.format(e))
        # raise e


def _delete_user_mgr_course(course_id, client):
    try:
        modified_course_id = course_id.replace('_', '_5F')
        course_manager_delete_url = test_data.urls.get('course_manager_url') + modified_course_id + '/delete/'
        course_manager_get_response = client.get(course_manager_delete_url)
        course_manager_payload = {
            'csrfmiddlewaretoken': course_manager_get_response.cookies['csrftoken'],
            'post': 'yes'
        }
        course_manager_delete_response = client.post(course_manager_delete_url, headers=headers_all,
                                                   data=course_manager_payload)
        if course_manager_delete_response.status_code == 200:
            LOGGER.info('Course Manager Course Deleted...')

    except Exception as e:
        LOGGER.error('Error in deleting the course from course manager table: {}'.format(e))
        raise


def _notify_slack(row, success_msg, failure_msg, success):
    try:
        company = CompanyCache.get_instance().get_attributes('company_id', int(row['company_id']))
        company = company.tli
    except:
        company = str(row['company_id'])

    msg_text = 'Company: {} - '.format(company)
    payload = {
        'username': SLACK_USER,
        'icon_emoji': ':no_entry:' if success else ':warning:',
        'text': msg_text + success_msg if success else msg_text + failure_msg,
        'link_names': None,
        'channel': '#eng-env-{}'.format(test_data.env),
        'attachments': None
    }
    payload['text'] += row['course_id']

    response = requests.post(SLACK_WEBHOOK, data=json.dumps(payload),
                    headers={'Content-Type': 'application/json'})

    if response.status_code != 200:
        raise RuntimeError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )


def delete_course(row):
    success_msg = 'Deletion Completed: '
    failure_msg = 'Deletion failed: '
    try:
        course_id = row['course_id']
        companycourse_id = _manta_query_companycourse_id(course_id)
        client = _delete_companycourse_id(companycourse_id)
        _delete_user_mgr_course(course_id, client)
        _manta_delete_row_courseImport(course_id)
        _manta_delete_row_CTACourse(course_id)
        _delete_cta_assets_s3(int(row['company_id']), course_id, row)
        LOGGER.info('COURSE DELETED...')
        _notify_slack(row, success_msg, failure_msg, success=True)
        return True
    except Exception as e:
        LOGGER.error(e)
        failure_msg = failure_msg + str(e)
        _notify_slack(row, success_msg, failure_msg, success=False)
        return e
