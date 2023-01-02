#!/usr/bin/env bash

# cd /data.nfs/ds114/baracus_full_tests/screenlogs/v1_beta_test1
# screen -L bash  /data.nfs/ds114/code/baracus/scripts/full_tests/run_full_tests_baracus.sh  ds114_test1 v1.0.0beta # <suffixoptional e.g. # _run2> and
# cd /data.nfs/ds114/baracus_full_tests/screenlogs/v1_beta_test2
# screen -L bash  /data.nfs/ds114/code/baracus/scripts/full_tests/run_full_tests_baracus.sh  ds114_test2 v1.0.0beta # <suffix optional>

ds_name=$1
sw_version=$2
suf=$3
echo Running ${ds_name} ${suf}

wd=/data.nfs/ds114/baracus_full_tests/${sw_version}${suf}

data_dir=${wd}/data
out_root_dir=${wd}/out

mkdir -p $data_dir
mkdir -p $out_root_dir

if [[ ! -d ${data_dir}/ds114_test1 ]]; then wget -c -O ${data_dir}/ds114_test1.tar "https://files.osf.io/v1/resources/9q7dv/providers/osfstorage/57e54a326c613b01d7d3ed90" && tar xf ${data_dir}/ds114_test1.tar -C ${data_dir}; fi
if [[ ! -d ${data_dir}/ds114_test2 ]]; then wget -c -O ${data_dir}/ds114_test2.tar "https://files.osf.io/v1/resources/9q7dv/providers/osfstorage/57e549f9b83f6901d457d162" && tar xf ${data_dir}/ds114_test2.tar -C ${data_dir}; fi
if [[ -e ${data_dir}/*.tar.gz ]]; then rm -r ${data_dir}/*.tar.gz; fi

in_dir=${data_dir}/${ds_name}
out_dir=${out_root_dir}/${ds_name}/baracus
fs_dir=${out_root_dir}/${ds_name}/freesurfer

mkdir -p $out_dir
chmod -R 777 $out_dir
mkdir -p $fs_dir
chmod -R 777 $fs_dir
cd $out_dir

cmd1="docker run --rm -ti \
-v ${in_dir}:/data/in \
-v ${out_dir}:/data/out \
-v ${fs_dir}:/data/freesurfer \
bids/baracus:${sw_version} \
/data/in /data/out participant \
--freesurfer_dir /data/freesurfer \
--license_key xxx \
--n_cpus 32"

cmd2="docker run --rm -ti \
-v ${in_dir}:/data/in \
-v ${out_dir}:/data/out \
-v ${fs_dir}:/data/freesurfer \
bids/baracus:${sw_version} \
/data/in /data/out group \
--freesurfer_dir /data/freesurfer \
--license_key xxx"


cmd3="tar -zcvf ${wd}/results_baracus_${sw_version}_${ds_name}${suf}.tar.gz ${out_dir}"

echo $cmd1 && $cmd1 && echo $cmd2 && $cmd2 && echo $cmd3 && $cmd3
