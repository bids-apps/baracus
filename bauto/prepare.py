import os
from subprocess import Popen, PIPE
import subprocess


# https://github.com/BIDS-Apps/freesurfer/blob/master/run.py#L12
def run(command, env={}, ignore_errors=False):
    merged_env = os.environ
    merged_env.update(env)
    # DEBUG env triggers freesurfer to produce gigabytes of files
    merged_env.pop('DEBUG', None)
    process = Popen(command, stdout=PIPE, stderr=subprocess.STDOUT, shell=True, env=merged_env)
    while True:
        line = process.stdout.readline()
        line = str(line, 'utf-8')[:-1]
        print(line)
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0 and not ignore_errors:
        raise Exception("Non zero return code: %d" % process.returncode)


def prepare_fs_data(fs_dir, out_dir, subject):
    out_files = downsample_surfs(fs_dir, out_dir, subject)
    out_files["aseg" + "_file"] = prepare_aseg(fs_dir, out_dir, subject)
    return out_files


def downsample_surfs(fs_dir, out_dir, subject, hemis=["lh", "rh"], meas=["thickness", "area"]):
    out_files = {}
    for m in meas:
        for h in hemis:
            subject_dir = os.path.join(out_dir, subject, "data")
            if not os.path.isdir(subject_dir):
                os.makedirs(subject_dir)
            out_file = os.path.join(subject_dir, "{h}.{m}.mgh".format(h=h, m=m))
            out_files[h + "_" + m + "_file"] = out_file

            cmd = "mris_preproc --s {subject} --target fsaverage4 --hemi {h} " \
                  "--meas {m} --out {out_file}".format(subject=subject, h=h, m=m, out_file=out_file)
            run(cmd, env={"SUBJECTS_DIR": fs_dir})
    return out_files


def prepare_aseg(fs_dir, out_dir, subject):
    subject_dir = os.path.join(out_dir, subject, "data")
    if not os.path.isdir(subject_dir):
        os.makedirs(subject_dir)
    out_file = os.path.join(subject_dir, "aseg")
    cmd = "asegstats2table --subjects {subject} --meas volume --tablefile {out_file}".format(subject=subject,
                                                                                             out_file=out_file)
    print(cmd)
    run(cmd, env={"SUBJECTS_DIR": fs_dir})
    return out_file


def run_prepare_all(freesurfer_dir, out_dir, subjects_to_analyze):
    # downsample surfaces to fsaverage4 and extract subcortical data from aseg
    fsav_dir = os.path.join(os.environ["FREESURFER_HOME"], "subjects")
    for fsav in ["fsaverage", "fsaverage4"]:
        if not os.path.exists(os.path.join(freesurfer_dir, fsav)):
            os.symlink(os.path.join(fsav_dir, fsav), os.path.join(freesurfer_dir, fsav))

    out_files = {}
    for subject in subjects_to_analyze:
        print("preparing %s" % subject)
        out_files[subject] = prepare_fs_data(freesurfer_dir, out_dir, "sub-" + subject)

    print("FINISHED prepared %s" % " ".join(subjects_to_analyze))
    return out_files
