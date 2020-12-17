import json
import logging
import argparse
import datetime
import os
import sys

# file_to_read = '/Users/paridhisaxena/Downloads/Course_json/proto/json/QA_ABI_LC_Lectora_M_C_N.json'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def _configure_logging(path_logger, log_filename):
    if not log_filename:
        log_filename = datetime.datetime.now().strftime('%Y-%m-%d') + '.log'
    fh = logging.FileHandler(filename=os.path.join(path_logger, log_filename), mode='w')
    fh.setLevel(logging.INFO)
    logger.addHandler(fh)

    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.INFO)
    logger.addHandler(sh)


def _create_argparser():
    parser = argparse.ArgumentParser()

    parser.add_argument('--file_path', required=True, type=str, help="path of the JSON")
    parser.add_argument('--path_to_log_file', type=str, default='', help='path to directory to write log file')
    parser.add_argument('--logfile_name', type=str, default='', help='logfile name, which could be course id')

    args = parser.parse_args()

    file_read = args.file_path
    file_to_save = args.path_to_log_file
    filename = args.logfile_name

    if not file_to_save:
        file_to_save = file_read.split(os.path.basename(file_read))[0]
        logger.info('Default value to save {}'.format(file_to_save))

    return file_read, file_to_save, filename


def _extract_nti(metadata):
    '''
     It processes the NTI data and create a dictionary with
    :key: a string of format 'motifType_motifStartIndex'; EXAMPLE: ELTS_16
    :value: a list of segmentType_subsegmentIndex associated with particular motif: ['1_76', '1_77', '1_78']
    :param metadata: course json
    :return: a dictionary
    '''
    try:
        metadata = json.loads(metadata)
        nti_data_motif = metadata['modules'][0]['units'][0]['contents'][0]['nti_data']
        dict_nti = {}
        for each_motif in nti_data_motif:
            motif_type = each_motif['properties_json']['motifType']
            for index, value in enumerate(each_motif['properties_json']['alternateContent']):
                slide_index = each_motif['properties_json']['altContIdx'][index]
                dict_key = motif_type + '_' + str(slide_index)  # ELTS_16
                dict_value = []
                for i in value:
                    segment_type = i['segment_type']
                    segment_index = i['segment_index']
                    dict_value.append('{}_{}'.format(segment_type, segment_index))
                dict_nti[dict_key] = dict_value
        return dict_nti
    except Exception as e:
        logger.error('Error in extracting the NTI data {}'.format(e))


def _extract_subsegments(metadata):
    '''
    It processes the course json to extract the sub-segments associated with each segment and put it in the dictionary
    :key: segment index
    :value: list containing all the sub-segments associated with the segment index with their segment type
    :param metadata: course json
    :return: dictionary
    '''
    dict_seg = {}
    try:
        metadata = json.loads(metadata)
        segments = metadata['modules'][0]['units'][0]['contents'][0]['segments']
        for each_segment in segments:
            key_dict = each_segment['index']
            key_value = []
            for each_subseg in each_segment['subsegments']:
                segment_type = each_subseg['segment_type']
                segment_index = each_subseg['segment_index']
                key_value.append('{}_{}'.format(segment_type, segment_index))
            dict_seg[key_dict] = key_value
        logger.debug(dict_seg)
        logger.info('Number of segments {}\n'.format(len(dict_seg)))
        return dict_seg    # {0: [], 1: ['1_0', '1_1', '1_2'], 2:...}
    except Exception as e:
        logger.error('Error in extracting the segments data {}'.format(e))


def _compare_subseg_nti(subseg, nti_data):
    for key, value in nti_data.items():
        motif_type, slide_index = key.split(sep='_')
        logger.info('Comparing {} of index {}'.format(motif_type, slide_index))
        index = int(slide_index)
        success = False
        while index >= 0 and success is False:
            logger.debug('value for the index {} is {}'.format(index, value))
            if set(value).issubset(subseg[index]):
                logger.info('Content is from the index: {}'.format(index))
                logger.info('Sub-segments involved are {}\n'.format(value))
                index -= 1
                success = True
            else:
                index -= 1

        if success is False:
            check_index = int(slide_index)
            while check_index < len(subseg) and success is False:
                if set(value).issubset(subseg[check_index]):
                    logger.info('Content is from the FUTURE index: {}'.format(check_index))
                    logger.info('Sub-segments involved are {}\n'.format(value))
                    check_index += 1
                    success = True
                else:
                    check_index += 1


def _read_file(file_to_read):
    with open(file_to_read, 'r') as f1:
        data = f1.read()
    return data


def compare_subsegment(data, path_to_save_file, log_filename):
    '''
    It is used when you want to import this script as package
    :param data: course json metadata
    :return:
    '''
    _configure_logging(path_to_save_file, log_filename)
    sub_seg = _extract_subsegments(data)
    sub_nti = _extract_nti(data)
    _compare_subseg_nti(sub_seg, sub_nti)


if __name__ == '__main__':
    read_json, file_to_write, filename = _create_argparser()
    _configure_logging(file_to_write, filename)

    data = _read_file(read_json)
    sub_seg = _extract_subsegments(data)
    sub_nti = _extract_nti(data)
    _compare_subseg_nti(sub_seg, sub_nti)
