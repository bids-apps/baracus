import os
import subprocess
from subprocess import Popen, PIPE


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


def run_fs_if_not_available(bids_dir, freesurfer_dir, subject_label, license_key, n_cpus, sessions=[], skip_missing=False):
    freesurfer_subjects = []
    if sessions:
        # long
        for session_label in sessions:
            freesurfer_subjects.append("sub-{sub}_ses-{ses}".format(sub=subject_label, ses=session_label))
    else:
        # cross
        freesurfer_subjects.append("sub-{sub}".format(sub=subject_label))

    fs_missing = False
    for fss in freesurfer_subjects:
        if not os.path.exists(os.path.join(freesurfer_dir, fss, "scripts/recon-all.done")):
            if skip_missing:
                freesurfer_subjects.remove(fss)
            else:
                fs_missing = True

    if fs_missing:
        cmd = "run_freesurfer.py {in_dir} {out_dir} participant " \
              "--hires_mode disable " \
              "--participant_label {subject_label} " \
              "--license_key {license_key} " \
              "--n_cpus {n_cpus} --steps cross-sectional".format(in_dir=bids_dir,
                                                                 out_dir=freesurfer_dir,
                                                                 subject_label=subject_label,
                                                                 license_key=license_key,
                                                                 n_cpus=n_cpus)

        print("Freesurfer for {} not found. Running recon-all: {}".format(subject_label, cmd))
        run(cmd)

    for fss in freesurfer_subjects:
        if not os.path.isfile(os.path.join(freesurfer_dir, fss, "stats/aseg.stats")):
            freesurfer_subjects.remove(fss)
    return freesurfer_subjects


def get_subjects_session(layout, participant_label, truly_longitudinal_study):
    valid_subjects = layout.get_subjects(modality="anat", type="T1w")
    freesurfer_subjects = []

    if participant_label:
        subjects_to_analyze = set(participant_label) & set(valid_subjects)
        subjects_not_found = set(participant_label) - set(subjects_to_analyze)

        if subjects_not_found:
            raise Exception("Requested subjects not found or do not have required data: {}".format(subjects_not_found))
    else:
        subjects_to_analyze = valid_subjects

    sessions_to_analyze = {}
    for subject in subjects_to_analyze:
        if truly_longitudinal_study:
            sessions = layout.get_sessions(modality="anat", type="T1w", subject=subject)
            sessions_to_analyze[subject] = sessions
            for session in sessions:
                freesurfer_subjects.append("sub-{sub}_ses-{ses}".format(sub=subject, ses=session))
        else:
            freesurfer_subjects.append("sub-{sub}".format(sub=subject))

    return subjects_to_analyze, sessions_to_analyze, freesurfer_subjects
