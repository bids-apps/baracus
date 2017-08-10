import os

from baracus.utils import run, run_fs_if_not_available


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


def run_prepare_all(bids_dir, freesurfer_dir, out_dir, subjects_to_analyze, sessions_to_analyze, n_cpus, license_key):
    """

    :param bids_dir:
    :param freesurfer_dir:
    :param out_dir:
    :param subjects_to_analyze:
    :param sessions_to_analyze: {"subject_label": ["test", "retest"],...}; {} if not truly_long_study
    :return:
    """

    fsav_dir = os.path.join(os.environ["FREESURFER_HOME"], "subjects")
    for fsav in ["fsaverage", "fsaverage4"]:
        if not os.path.exists(os.path.join(freesurfer_dir, fsav)):
            os.symlink(os.path.join(fsav_dir, fsav), os.path.join(freesurfer_dir, fsav))

    # check if freesurfer is available and run if missing
    freesurfer_subjects = []
    for subject in subjects_to_analyze:
        sessions = sessions_to_analyze.get(subject)
        freesurfer_subjects.append(run_fs_if_not_available(bids_dir, freesurfer_dir, subject, license_key, n_cpus,
                                                       sessions))

    # downsample surfaces to fsaverage4 and extract subcortical data from aseg
    out_files = {}
    for fs_subject in freesurfer_subjects:
        print("preparing %s" % subject)
        out_files[fs_subject] = prepare_fs_data(freesurfer_dir, out_dir, fs_subject)

    print("FINISHED. Prepared %s" % " ".join(freesurfer_subjects))
    return out_files
