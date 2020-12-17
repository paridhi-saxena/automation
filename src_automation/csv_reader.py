import csv
import datetime
import os
import tempfile
import logging
import boto3 as boto
from pathlib import Path
import subprocess
import test_data as td
from course_delete import delete_course

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
for name in logging.Logger.manager.loggerDict.keys():
    if ('boto' in name) or ('urllib3' in name):
        logging.getLogger(name).setLevel(logging.WARNING)


class CourseImport:

    def valid_row(self, row_dict):

        keys_dict = ['course_id', 'company_id', 'course_zip', 'completed']
        is_valid = True
        for each_key in keys_dict:
            if row_dict[each_key] is None or len(row_dict[each_key]) <= 0:
                LOGGER.error("*********************************************************")
                LOGGER.error('{} key must have valid value' .format(each_key))
                LOGGER.error('Edit the CSV and try again')
                LOGGER.error("*********************************************************")
                is_valid = False
        return is_valid

    def check_status(self, row_dict):
        check_go = False
        if int(row_dict['completed']) == 0:
            check_go = self.valid_row(row_dict)
        return check_go

    def is_verbose(self, row):
        if int(row['verbose']) == 1:
            LOGGER.setLevel(logging.DEBUG)

    def is_nti(self, row_dict):
        enable_nti = False
        nti_background = None
        nti_fonts = None
        if int(row_dict['with_nti']) == 1:
            enable_nti = True

            if len(row_dict['nti_background']) > 0:
                nti_background = str(row_dict['nti_background'])

            if len(row_dict['nti_fonts']) > 0:
                nti_fonts = str(row_dict['nti_fonts'])

        return enable_nti, nti_background, nti_fonts

    def is_measurement(self, row_dict):
        enable_measurements = True
        if int(row_dict['measurements']) == 0:
            enable_measurements = False
        return enable_measurements

    def is_cta(self, row_dict):
        enable_cta = False
        path_sup_docs = None
        cta_doc_label = None
        min_pl = None
        max_pl = None

        if int(row_dict['with_cta']) == 1:
            enable_cta = True

            if len(row_dict['sup_docs']) > 0:
                path_sup_docs = str(row_dict['sup_docs'])

                if len(row_dict['sup_doc_label']) > 0:
                    cta_doc_label = str(row_dict['sup_doc_label'])
                else:
                    cta_doc_label = 'Regulation_Doc'

            if int(row_dict['min_phrase_length']) is not None:
                min_pl = row_dict['min_phrase_length']

            if int(row_dict['max_phrase_length']) is not None:
                max_pl = row_dict['max_phrase_length']
        return enable_cta, min_pl, max_pl, path_sup_docs, cta_doc_label

    def download_s3_local(self, prefix, bucketname, profile_name, download_folder, write_row=None, row=None):

        session = boto.Session()
        profile_list = session.available_profiles
        if len(profile_list) > 0:
            boto_session = boto.Session(profile_name=profile_name)
        else:
            boto_session = boto.Session()
        s3_resource = boto_session.resource('s3')
        destdir = download_folder
        basename = prefix
        dest = os.path.join(destdir, basename)
        path = Path(dest)
        try:
            if not path.parent.exists():
                path.parent.mkdir(parents=True)
        except OSError as e:
            LOGGER.error(e)
        try:
            s3_resource.Bucket(bucketname).download_file(prefix, dest)
        except Exception as e:
            LOGGER.error("EXCEPTION IN DOWNLOADING FOR BUCKET: {} AND PREFIX: {} is: {}".format(bucketname, prefix, e))
            row['completed'] = -1
            row['error_msg'] = "EXCEPTION IN DOWNLOADING FOR BUCKET: " + bucketname + " AND PREFIX: " + prefix
            self.write_csv(write_row, row)
        return dest

    def upload_files_s3(self, bucketname, localpath, base_s3_key, profile_name):

        # local environments will have profiles
        #  provisioned environments will not
        session = boto.Session()
        profile_list = session.available_profiles
        if len(profile_list) > 0:
            boto_session = boto.Session(profile_name=profile_name)
        else:
            boto_session = boto.Session()

        s3 = boto_session.resource('s3')
        bucket = s3.Bucket(bucketname)

        if os.path.isfile(localpath):
            with open(localpath, 'rb') as data:
                key_path = os.path.join(base_s3_key, os.path.basename(localpath))
                bucket.put_object(Key=key_path, Body=data)

    def compose_cmd_line_args(self, each_row, write_row, path_temp_folder):

        command = str(td.data.get('command'))
        path_script = str(td.data.get('path_script'))
        company_id = str(each_row['company_id'])
        key_file = str(td.data.get('key_file'))
        api_protocol = str(td.data.get('api_protocol'))
        api_port = str(td.data.get('api_port'))
        api_host = str(td.data.get('api_host'))

        bucketname = td.data.get('bucketname')
        profile_name = td.data.get('profile_name')
        zip_path = td.data.get('zip_path') + each_row['course_zip']
        path_course_zip = self.download_s3_local(zip_path, bucketname, profile_name, path_temp_folder, each_row, write_row)
        LOGGER.debug('path of the zip file: {}'.format(path_course_zip))
        list_cmd_args = []

        if os.path.exists(path_course_zip) and \
                os.path.isfile(path_course_zip) and os.path.getsize(path_course_zip) > 0:

            LOGGER.info("IMPORTING THE COURSE... ")

            list_cmd_args.append(command)  # command
            list_cmd_args.append(path_script)  # path to the manual course importer script.
            list_cmd_args.append('--company_id')
            list_cmd_args.append(company_id)  # company id
            list_cmd_args.append('--key_file')
            list_cmd_args.append(key_file)  # key_file
            list_cmd_args.append('--api_protocol')
            list_cmd_args.append(api_protocol)  # api_protocol
            list_cmd_args.append('--api_port')
            list_cmd_args.append(api_port)  # api_port
            list_cmd_args.append('--api_host')
            list_cmd_args.append(api_host)  # api_host

            enable_nti, nti_background, nti_fonts = self.is_nti(each_row)

            if enable_nti is True:
                list_cmd_args.append('--with_nti')

                if nti_background is not None:
                    path_image = self.download_s3_local(nti_background, bucketname, profile_name,
                                                          path_temp_folder)
                    if os.path.exists(path_image) and \
                            os.path.isfile(path_image) and os.path.getsize(path_image) > 0:
                        list_cmd_args.append('--nti_background')
                        list_cmd_args.append(path_image)

                if nti_fonts is not None:
                    list_cmd_args.append('--nti_fonts')
                    list_cmd_args.append(nti_fonts)

            enable_cta, min_pl, max_pl, path_sup_docs, cta_doc_label = self.is_cta(each_row)

            if enable_cta is True:
                list_cmd_args.append('--with_cta')

                if min_pl is not None:
                    list_cmd_args.append('--min_cta_phrase_length')
                    list_cmd_args.append(str(min_pl))

                if max_pl is not None:
                    list_cmd_args.append('--max_cta_phrase_length')
                    list_cmd_args.append(str(max_pl))

                if path_sup_docs is not None:
                    path_doc = self.download_s3_local(path_sup_docs, bucketname, profile_name,
                                                        path_temp_folder)
                    if os.path.exists(path_doc) and \
                            os.path.isfile(path_doc) and os.path.getsize(path_doc) > 0:
                        list_cmd_args.append('--sup_docs')
                        list_cmd_args.append(path_doc)

                if cta_doc_label is not None:
                    list_cmd_args.append('--sup_docs_label')
                    list_cmd_args.append(cta_doc_label)

            if self.is_measurement(each_row) is False:
                list_cmd_args.append('--without_measurements')

            if int(each_row['verbose']) == 1:
                list_cmd_args.append('-v')

            list_cmd_args.append(path_course_zip)  # last argument
        return list_cmd_args, path_course_zip

    def import_course(self, row, write_row, path_temp_folder):

        cmd_args_list, path_zip = self.compose_cmd_line_args(row, write_row, path_temp_folder)

        # LOGGER.debug( 'my current path is: ', os.getcwd())
        LOGGER.debug('Project Path is: {}'.format(os.environ.get("PROJPATH")))

        LOGGER.info('CMD line arguments: {}\n'.format(str(cmd_args_list)))
        try:
            res = subprocess.run(cmd_args_list, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output_data = (res.stdout).decode('utf-8')

            LOGGER.info(output_data)

            row = self.read_output(write_row, row, output_data, path_zip, path_temp_folder)
            return row

        except Exception as e:
            LOGGER.error(e)
            raise e

    def read_output(self, write_row, row, result_data='', path_zip=None, path_temp_folder=''):

        success_msg = 'INFO:manual_course_importer:Course zip ({}) has successfully been submitted for import'.format(path_zip)
        error_msg = 'ERROR:manual_course_importer:'

        if success_msg in result_data:
            row['completed'] = 1
            row['error_msg'] = ''
        elif error_msg in result_data:
            row, delete = self.inspect_error_msg(result_data, row)
            if row['completed'] == str(0) and delete is True:
                row = self.reimport_course(row, write_row, path_temp_folder)
            else:
                row['completed'] = -1
        return row

    def write_csv(self, write_row, read_row):
        write_row.writerow(read_row)

    def inspect_error_msg(self, result_data, row):
        error_string = ''
        data_list = result_data.split('\n')
        for each_line in data_list:
            if 'ERROR:manual_course_importer:' in each_line:
                error_string = error_string + each_line
            row['error_msg'] = error_string
        err_response_1 = 'A course of that ID is already being imported'
        err_response_2 = 'Course ID already exists in database:'
        if err_response_1 in error_string or err_response_2 in error_string:
            delete = True
        else:
            delete = False
        return row, delete

    def reimport_course(self, row, write_row, path_temp_folder):
        try:
            is_delete = delete_course(row)
            if is_delete is not True:
                row['completed'] = -1
                row['error_msg'] = is_delete
                LOGGER.error('Marking the course with Error\n')
            else:
                LOGGER.info('Trying to re-import the course again...\n')
                row = self.import_course(row, write_row, path_temp_folder)
            return row
        except Exception as e:
            raise e

    def download_read_csv(self):

        with tempfile.TemporaryDirectory() as path_temp_folder:

            prefix = td.data.get('prefix')
            bucketname = td.data.get('bucketname')
            profile_name = td.data.get('profile_name')
            header = td.data.get('header')

            path_csv = self.download_s3_local(prefix, bucketname, profile_name, path_temp_folder)
            path_csv_writer = path_temp_folder + '/test/import_automation_new.csv'
            LOGGER.debug('temp folder is: {}'.format(path_temp_folder))

            try:
                if os.path.exists(path_csv):

                    with open(path_csv, 'r') as file_csv, open(path_csv_writer, 'w') as file_csv1:
                        data_csv = csv.DictReader(file_csv)
                        write_row = csv.DictWriter(file_csv1, fieldnames=header)
                        write_row.writeheader()

                        for row in data_csv:
                            self.is_verbose(row)
                            LOGGER.debug(row)

                            is_process = self.check_status(row)

                            if is_process is False:
                                self.write_csv(write_row, row)
                            else:
                                try:
                                    row = self.import_course(row, write_row, path_temp_folder)
                                    self.write_csv(write_row, row)
                                except Exception as e:
                                    row['error_msg'] = e
                                    row['completed'] = -1
                                    self.write_csv(write_row, row)

                os.rename(path_csv_writer, path_csv)
                base_s3_key = td.data.get('base_s3_key')
                self.upload_files_s3(bucketname, path_csv, base_s3_key, profile_name)

            except Exception as e:
                LOGGER.error(e)


if __name__ == '__main__':

    LOGGER.info("..........  Begin processing: {}\n" .format(str(datetime.datetime.now())))

    obj1 = CourseImport()
    obj1.download_read_csv()

    LOGGER.info("............  Done processing: {}\n" .format(str(datetime.datetime.now())))
