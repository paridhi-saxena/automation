#!/bin/bash
#source myenv/bin/activate
#before running this script make sure to run the sql_scripts.txt to create the course records that will be cancelled

export PROJPATH=$(pwd)
echo ''
echo "project path is: "  $PROJPATH
echo ''

source $PROJPATH/.venv/bin/activate
echo "Using python: "
python --version

env="proto"
echo "env set is " $env
cd ~
. .manatee_venv/bin/activate
cd manatee/tools

if [ ${env} == dev ];
then
    echo "env is dev"
    companyid="63"
    non_existing_companyid="101"
    cancel_course_ph1="MICRO_VIDEO_1_cancel"
    cancel_course_ph2="MICRO_VIDEO_2_cancel"
    cancel_course_ph0="MICRO_VIDEO_0_cancel"
    cancel_course_ph100="MICRO_VIDEO_100_cancel"
    cancel_course_nonexg="NON_EXTG"
elif [ ${env} == proto ];
then
    echo "env is proto"
    companyid="1"
    non_existing_companyid="101"
    cancel_course_ph1="MICRO_VIDEO_1_cancel"
    cancel_course_ph2="MICRO_VIDEO_2_cancel"
    cancel_course_ph0="MICRO_VIDEO_0_cancel"
    cancel_course_ph100="MICRO_VIDEO_100_cancel"
    cancel_course_nonexg="NON_EXTG"
elif [ ${env} == staging ];
then
    echo "env is staging"
    companyid="58"
    non_existing_companyid="101"
    cancel_course_ph1="MICRO_VIDEO_1_cancel"
    cancel_course_ph2="MICRO_VIDEO_2_cancel"
    cancel_course_ph0="MICRO_VIDEO_0_cancel"
    cancel_course_ph100="MICRO_VIDEO_100_cancel"
    cancel_course_nonexg="NON_EXTG"
else
   echo "non supported environment or env does not exist"
fi


echo "cancelling a non existent course"
python3 manual_course_importer.py  --company_id $companyid   --key_file ../devkey_private.key   --api_protocol https   --api_port 443   --api_host management.$env.test.com  --cancel $cancel_course_nonexg

echo "cancelling a phase 100 course"
python3 manual_course_importer.py  --company_id $companyid   --key_file ../devkey_private.key   --api_protocol https   --api_port 443   --api_host management.$env.test.com  --cancel $cancel_course_ph100

echo "cancelling a phase 0 course"
python3 manual_course_importer.py  --company_id $companyid   --key_file ../devkey_private.key   --api_protocol https   --api_port 443   --api_host management.$env.test.com  --cancel $cancel_course_ph0

echo "cancelling a phase -1 course"
python3 manual_course_importer.py  --company_id $companyid   --key_file ../devkey_private.key   --api_protocol https   --api_port 443   --api_host management.$env.test.com  --cancel $cancel_course_ph1

echo "cancelling a phase -2 course"
python3 manual_course_importer.py  --company_id $companyid   --key_file ../devkey_private.key   --api_protocol https   --api_port 443   --api_host management.$env.test.com  --cancel $cancel_course_ph2

echo "cancelling a non existent company course"
python3 manual_course_importer.py  --company_id $non_existing_companyid   --key_file ../devkey_private.key   --api_protocol https   --api_port 443   --api_host management.$env.test.com  --cancel $cancel_course_nonexg

