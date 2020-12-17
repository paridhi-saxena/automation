import os

env = os.environ.get('ENVIRONMENT')
csv_filename = env + '_import_automation.csv'

data = dict(prefix='test/{}'.format(csv_filename),
            bucketname='sqa-course-ingestion',
            profile_name='testmock',
            zip_path='test/course_zip_files/',
            command='python3',
            path_script='/home/ubuntu/manatee/tools/manual_course_importer.py',
            key_file='/home/ubuntu/manatee/devkey_private.key',
            api_protocol='https',
            api_port='443',
            api_host='management.{}.test.com'.format(env),
            base_s3_key='test',
            header=['course_zip', 'course_id', 'company_id', 'measurements', 'with_cta', 'min_phrase_length',
                    'max_phrase_length', 'with_nti', 'nti_background', 'nti_fonts', 'sup_doc_label', 'sup_docs',
                    'verbose', 'completed', 'error_msg'])

urls = {
    'base_url_backend': 'https://backend.{}.test.com/kraken/'.format(env),
    'login_url': 'https://backend.{}.test.com/kraken/login/?next=/kraken/'.format(env),
    'company_course_url': 'https://backend.{}.test.com/kraken/user_management/companycourse/'.format(env),
    'course_manager_url': 'https://backend.{}.test.com/kraken/course_manager/course/'.format(env),
}

headers_all = {
    'Referer': 'https://backend.{}.test.com/kraken/'.format(env)
}

DB_CONFIG = {
     'host': '',
     'port': None,
     'user': '',
     'password': '',
     'db': ''
}

body_post = {
    'username': 'paridhi.saxena@test.com',
    'password': 'passW0rd12',
    'this_is_the_login_form': '1',
    'next': '/kraken/'
}

cta_data = {
    'bucketname': 'test-{}-dashboard'.format(env),
    'profile_name': 'testmock'
}
