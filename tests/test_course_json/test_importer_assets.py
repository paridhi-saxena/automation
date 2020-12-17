import os
import json
import logging
import pytest
from tool_download_course_json import download_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


"""
this utility compare the recent imported course json with json of the same course but previous import.
:test_json: the recent imported course json
:refer_json: json of other version of the same course

"""

path = '/home/ubuntu/squid/course-importer-validator/course_json'


class TestCourseJson(object):

    @pytest.fixture(scope='session')
    def _download_read_json(self, request):
        course_id_list = request.config.getoption("--course_id")
        course_download = course_id_list[0]
        try:
            test_json = download_json(course_download, path)
        except Exception as e:
            raise e
        refer_json = os.path.join(path, 'refer_json', course_id_list[1]) + '.json'
        try:
            print('Test JSON {}'.format(test_json))
            print('Refer JSON {}'.format(refer_json))

            with open(test_json, 'r') as f1:
                test_data = f1.read()
                test_data = json.loads(test_data)

            with open(refer_json, 'r') as f2:
                refer_data = f2.read()
                refer_data = json.loads(refer_data)
            return test_data, refer_data
        except Exception as e:
            raise e

    def collect_tier_values(self, course_dict, target_tier, target_key):
        dict_values = {}

        for module_index, module in enumerate(course_dict['modules']):
            print(type(module))
            if target_tier == 'modules':
                dict_values[module_index] = module[target_key]
                continue
            for unit_index, unit in enumerate(module['units']):
                if target_tier == 'units':
                    dict_values[unit_index] = unit[target_key]
                    continue
                for content_index, content in enumerate(unit['contents']):
                    if target_tier == 'contents':
                        index = str(unit_index) + '_' + str(content_index)
                        dict_values[index] = content[target_key]
                        continue
                    if target_tier == 'segments':
                        for segment_index, segment in enumerate(content['segments']):
                            index = str(unit_index) + '_' + str(content_index) + '_' + str(segment_index)
                            dict_values[index] = segment[target_key]
                            continue
                    elif target_tier == 'questions':
                        for question_index, question in enumerate(content['questions']):
                            index = str(unit_index) + '_' + str(content_index) + '_' + str(question_index)
                            dict_values[index] = question[target_key]
                            continue
                    elif target_tier == 'nti_data':
                        for nti_index, nti in enumerate(content['nti_data']):
                            index = str(unit_index) + '_' + str(content_index) + '_' + str(nti_index)
                            dict_values[index] = nti[target_key]
                            continue
                    else:
                        raise Exception('Tier {} was never found in course_json!'.format(target_tier))
        return dict_values

    def ets_in_range(self, t_x, r_y):
        if abs(t_x - r_y) <= 0.10 * r_y:
            return True
        else:
            return False

    def test_key_items(self, _download_read_json):
        test_data, refer_data = _download_read_json
        print('i am testing')
        list_keys = ['id', 'title', 'group', 'description', 'modules', 'course_options', 'version', 'division',
                     'department', 'company_id', 'company_name', 'company_tli', 'domain_id', 'generate_offline_zip',
                     'offline_package_location', 'offline_package_location']
        for each_key in list_keys:
            print('{}: {}'.format(each_key, test_data[each_key]))

    def test_module_length(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_module = test_data['modules']
        refer_module = refer_data['modules']
        print('Module Length: {}'.format(len(test_module)))
        assert len(test_module) == len(refer_module)

    def test_unit_length(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_unit = test_data['modules'][0]['units']
        refer_unit = refer_data['modules'][0]['units']
        print('Unit Length: {}'.format(len(test_unit)))
        assert len(test_unit) == len(refer_unit)

    def test_content_length(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_dict = self.collect_tier_values(test_data, 'units', 'contents')
        refer_dict = self.collect_tier_values(refer_data, 'units', 'contents')
        print('Content_Length: {}'.format(len(test_dict)))
        print('Content_Length: {}'.format(len(refer_dict)))
        assert test_dict == refer_dict

    def test_segments_length(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_segments = self.collect_tier_values(test_data, 'contents', 'segments')
        refer_segments = self.collect_tier_values(refer_data, 'contents', 'segments')
        assert len(test_segments) == len(refer_segments)

    def test_segment_text(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'segments', 'text')
        refer_text = self.collect_tier_values(test_data, 'segments', 'text')
        # print(refer_text)
        assert test_text == refer_text

    def test_external_ids(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'segments', 'external_id')
        refer_text = self.collect_tier_values(test_data, 'segments', 'external_id')
        assert test_text == refer_text

    def test_segment_ets(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'segments', 'ets')
        refer_text = self.collect_tier_values(refer_data, 'segments', 'ets')
        try:
            assert test_text == refer_text
        except AssertionError:
            key_list = []
            result = False
            for key in test_text:
                if test_text[key] != refer_text[key]:
                    result = self.ets_in_range(test_text[key], refer_text[key])
                    if result is False:
                        key_list.append(key)
            print('Number of ETS not matched is {}'.format(len(key_list)))
            assert result

    def test_content_type(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'contents', 'type')
        refer_text = self.collect_tier_values(refer_data, 'contents', 'type')
        assert test_text == refer_text

    def test_content_type_version(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'contents', 'type_version')
        refer_text = self.collect_tier_values(refer_data, 'contents', 'type_version')
        assert test_text == refer_text

    def test_content_package_type(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'contents', 'package_type')
        refer_text = self.collect_tier_values(refer_data, 'contents', 'package_type')
        assert test_text == refer_text

    def test_content_length_field(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'contents', 'length')
        refer_text = self.collect_tier_values(refer_data, 'contents', 'length')
        assert test_text == refer_text

    def test_content_scorm_interactions(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'contents', 'scorm_interactions')
        refer_text = self.collect_tier_values(refer_data, 'contents', 'scorm_interactions')
        assert test_text == refer_text

    def test_content_scorm_quiz_score(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'contents', 'scorm_quiz_score')
        refer_text = self.collect_tier_values(refer_data, 'contents', 'scorm_quiz_score')
        assert test_text == refer_text

    def test_questions_length(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'contents', 'questions')
        refer_text = self.collect_tier_values(refer_data, 'contents', 'questions')
        assert len(test_text) == len(refer_text)

    def test_questions_text(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'questions', 'text')
        refer_text = self.collect_tier_values(refer_data, 'questions', 'text')
        assert test_text == refer_text

    def test_questions_title(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'questions', 'title')
        refer_text = self.collect_tier_values(refer_data, 'questions', 'title')
        assert test_text == refer_text

    def test_questions_index(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'questions', 'index')
        refer_text = self.collect_tier_values(refer_data, 'questions', 'index')
        assert test_text == refer_text

    def test_questions_type(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'questions', 'type')
        refer_text = self.collect_tier_values(refer_data, 'questions', 'type')
        assert test_text == refer_text

    def test_scorm_question_id(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'questions', 'scorm_question_id')
        refer_text = self.collect_tier_values(refer_data, 'questions', 'scorm_question_id')
        assert test_text == refer_text

    def test_unit_number_of_motifs(self, _download_read_json):
        test_data, refer_data = _download_read_json
        test_text = self.collect_tier_values(test_data, 'contents', 'nti_data')
        refer_text = self.collect_tier_values(refer_data, 'contents', 'nti_data')
        assert len(test_text) == len(refer_text)

    def test_course_options_length(self, _download_read_json):
        test_data, refer_data = _download_read_json
        course_options_test = test_data['course_options']
        course_options_refer = refer_data['course_options']
        assert len(course_options_refer) == len(course_options_test) == 3

    def test_course_version(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert test_data['version'] is not None

    def test_course_division(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert test_data['division'] is not None

    def test_course_department(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert test_data['department'] is not None

    def test_course_company_id(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert type(test_data['company_id']) is int

    def test_course_company_name(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert test_data['company_name'] is not None

    def test_course_company_tli(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert test_data['company_tli'] is not None

    def test_course_company_domain_id(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert type(test_data['domain_id']) is int

    def test_course_generate_offline_zip(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert type(test_data['generate_offline_zip']) is bool

    def test_course_numeric_id(self, _download_read_json):
        test_data, refer_data = _download_read_json
        assert type(test_data['numeric_id']) is int

    def test_nti_if_nti_enable(self, _download_read_json):
        test_data, refer_data = _download_read_json
        course_options = test_data['course_options']
        nti = course_options['nti']['enabled']
        if nti:
            assert test_data['modules'][0]['units'][0]['contents'][0]['nti_data']

    def test_random_seed_nti(self, _download_read_json):
        test_data, refer_data = _download_read_json
        course_options = test_data['course_options']
        nti = course_options['nti']['enabled']
        if nti:
            assert course_options['nti']['random_seed'] is int

    def test_random_seed_cta(self, _download_read_json):
        test_data, refer_data = _download_read_json
        course_options = test_data['course_options']
        cta = course_options['cta']['enabled']
        if cta:
            assert course_options['cta']['random_seed'] is int