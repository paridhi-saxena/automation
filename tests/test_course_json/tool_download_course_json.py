import json
import os
import argparse
import logging
import manta
from manta.util.sessions.CompanySessionManager import CompanySessionManager
from manta.models.platform.course_import.ImportStatus import ImportStatus
from compare_subsegments import compare_subsegment

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {'host': os.environ.get('PLATFORM_DB_HOST'),
             'port': os.environ.get('PLATFORM_DB_PORT'),
             'user': os.environ.get('PLATFORM_DB_USER'),
             'password': os.environ.get('PLATFORM_DB_PASS'),
             'db': os.environ.get('PLATFORM_DB')}

manta.initialize(
    platform_db_settings=DB_CONFIG,
    populate_caches=[],
    uwsgi_mode=False
)

sm = CompanySessionManager.get_instance()


def _extract_alt_content(metadata):
    metadata = json.loads(metadata)
    nti_data_motif = metadata['modules'][0]['units'][0]['contents'][0]['nti_data']
    if nti_data_motif:
        collected_motifs = {}
        for each_motif_type in nti_data_motif:
            motif_id = each_motif_type['properties_json']['motifType'] + '_' + str(each_motif_type['numeric_id'])
            motif_content = {}
            for index, value in enumerate(each_motif_type['properties_json']['alternateContent']):
                slide_id = each_motif_type['properties_json']['altContIdx'][index]
                slide_nti_content = []
                for i in value:   # value is the one remediation slide content.
                    segment_type = i['segment_type']
                    slide_nti_content.append('[{}]'.format(segment_type) + ' * '.join(i['content']))
                motif_content[slide_id] = slide_nti_content  # key = slide_id with its content as value.
            collected_motifs[motif_id] = motif_content
        return collected_motifs
    else:
        logger.info('Skipping writing NTI as No NTI data found for the course')


def _write_course_json(metadata, each_course, path):
    path_dir = os.path.join(path, 'course_json/json/')
    _make_dir(path_dir)
    try:
        filename = path_dir + each_course + '.json'
        with open(filename, 'w') as f1:
            f1.write(metadata)
        return filename
    except Exception as e:
        logger.error('Error in Writing the JSON for the course {} is {}' .format(each_course, e))
        raise e


def _make_dir(path_dir):
    if not os.path.exists(path_dir):
        try:
            os.makedirs(path_dir)
        except OSError as e:
            logger.error(e)
            raise e


def _write_nti_extract(motifs, each_course, path, metadata):
    try:
        path_dir = os.path.join(path, 'course_json/nti_extract/')
        _make_dir(path_dir)
        filename = path_dir + each_course + '_nti_extract.txt'
        with open(filename, 'w') as f1:
            for key, value in motifs.items():
                f1.write('_' * 20 + '\n')
                f1.write(key + '\n')
                for k, v in value.items():
                    f1.write(' ' * 12 + "SLIDE %s \n" % k)
                    for lines in v:
                        f1.write('- %s' % lines + '\n')
                    f1.write('. ' * 20 + '\n')
                f1.write('_' * 20 + '\n')
        compare_subsegment(metadata, path_dir, each_course)
    except Exception as e:
        logger.error('Error in Writing the NTI extract for the course {} is {}' .format(each_course, e))
        raise e


def _write_full_text(metadata_json, each_course, path):

    logger.info(type(metadata_json))
    segments = metadata_json['modules'][0]['units'][0]['contents'][0]['segments']
    full_texts = []

    for each_seg in segments:
        full_text = '\n'.join((' '.join(each_seg['text']),
                              '\n'.join(each_seg['transcribed_text'])))
        full_texts.append(full_text)
    try:
        path_dir = os.path.join(path, 'course_json/full_text/')
        _make_dir(path_dir)
        filename = path_dir + each_course + '_full_text.txt'
        with open(filename, 'w') as f1:
            for index, each_text in enumerate(full_texts):
                f1.write('\n' + '*' * 20 + str(index) + '*' * 20 + '\n')
                f1.write(each_text)
    except Exception as e:
        logger.error('Error in Writing the FULL TEXT for the course {} is {}' .format(each_course, e))
        raise e


def download_json(each_course, path):
    try:
        with sm.get_platform_engine_session() as sesh:
            q = sesh.query(ImportStatus)
            q = q.filter(ImportStatus.course_id == each_course)
            row = q.one()
            try:
                metadata_json = json.loads(row.json)
                metadata = json.dumps(metadata_json, indent=2)
                filename_path = _write_course_json(metadata, each_course, path)
                _write_full_text(metadata_json, each_course, path)
                motifs = _extract_alt_content(metadata)
                if motifs:
                    _write_nti_extract(motifs, each_course, path, metadata)
                return filename_path
            except Exception as e:
                logger.error(e)
                raise e
    except Exception as e:
        logger.error('Error in finding the JSON from Import Status Table: {}'.format(e))
        raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--course_id',  nargs='+', help="List of course ids")
    parser.add_argument('--path', type=str, default='.', help='Provide the path to download the json')
    args = parser.parse_args()
    for each_course in args.course_id:
        download_json(each_course, args.path)
