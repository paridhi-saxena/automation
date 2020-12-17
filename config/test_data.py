import os
from pathlib import Path

# -*- coding: utf-8 -*-


######## data for UI tests ########
proj_base = Path(os.path.dirname(os.path.abspath(__file__))).parent
print("project base : ", proj_base)
os.environ['PROJ_BASE'] = str(proj_base)

env = os.getenv('S3_ENV', "proto") # keep this at proto while checking in code

profile_name = os.getenv('S3_PROFILE')
bucket_name_input = os.getenv('S3_INPUT_BUCKET', 'input')
bucket_name_output = os.getenv('S3_OUTPUT_BUCKET', 'output')

bucketname_junkdrawer = os.getenv('S3_JUNK_DRAWER_BUCKET','ops-junk-drawer')


s3_data_folder = os.path.join(str(proj_base), "importer_data", '')
base_data = os.path.join(str(proj_base), "data", env, '')
base_results = os.path.join(str(proj_base), "results", env, '')
base_data_set = str(proj_base) + str(os.getenv('BASE_S3_DATA_PATH','/data/%s/'%env))


