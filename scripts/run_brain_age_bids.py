#! /usr/bin/env python

import argparse
import os
from glob import glob
import pandas as pd
from pkg_resources import resource_filename, Requirement
from baracus.predict import predict_brain_age_single_subject
from baracus.prepare import run_prepare_all
from baracus import models_list
import re

if __name__ == "__main__":
    __version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'version')).read()

    parser = argparse.ArgumentParser(description='BARACUS: Brain-Age Regression Analysis and Computation Utility Software. BIDS mode. '
                                                 'You specify a BIDS-formatted freesurfer folder as input. All data '
                                                 'is extracted automatiacally from that folder. ')
    parser.add_argument('freesurfer_dir', help='Folder with freesurfer subjects formatted according to BIDS '
                                               'standard.')
    parser.add_argument('out_dir', help='Results are put here.')
    parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                                               '"participant": predicts single subject brain age, '
                                               '"group": collects single subject predictions.',
                        choices=['participant', 'group'])

    parser.add_argument('--participant_label', help='The label of the participant that should be analyzed. The label '
                                                    'corresponds to sub-<participant_label> from the BIDS spec '
                                                    '(so it does not include "sub-"). If this parameter is not '
                                                    'provided all subjects should be analyzed. Multiple '
                                                    'participants can be specified with a space separated list.',
                        nargs="+")
    parser.add_argument('--models', choices=models_list, default=["Liem2016__OCI_norm"], help='',
                        nargs="+")
    parser.add_argument('-v', '--version', action='version',
                        version='BIDS-App example version {}'.format(__version__))


    args = parser.parse_args()

    model_dir = resource_filename(Requirement.parse("baracus"), 'models')
    subject_dirs = []
    if args.participant_label:
        for pl in args.participant_label:
            subject_dirs += [os.path.basename(s) for s in sorted(glob(os.path.join(args.freesurfer_dir,
                                                                      "sub-" + pl + "*")))]
    else:
        subject_dirs = [os.path.basename(s) for s in sorted(glob(os.path.join(args.freesurfer_dir, "sub-*")))]

    # if longitudinal subjects, only take crossectional ses subjects and skip long and base subjects
    if list(filter(re.compile(r".long.").search, subject_dirs)):  # longitudinal subjects
        ses_subjects = list(filter(re.compile(r"_ses-").search, subject_dirs))
        subjects_to_analyze = [s for s in ses_subjects if not ".long." in s]
    else:
        subjects_to_analyze = subject_dirs


    if args.analysis_level == "participant":
        data_files = run_prepare_all(args.freesurfer_dir, args.out_dir, subjects_to_analyze)

        for subject, d in data_files.items():
            d["out_dir"] = args.out_dir
            d["model_dir"] = model_dir
            d["models"] = args.models
            d["subject_label"] = subject
            predict_brain_age_single_subject(**d)

    elif args.analysis_level == "group":
        print("Creating group table...")
        df = pd.DataFrame([])
        for subject in subjects_to_analyze:
            in_file = os.path.join(args.out_dir, subject, subject + "_predicted_age.tsv")
            df = df.append(pd.read_csv(in_file, sep="\t"))

        group_out_dir = os.path.join(args.out_dir, "00_group")
        if not os.path.isdir(group_out_dir):
            os.makedirs(group_out_dir)
        out_file = os.path.join(group_out_dir, "group_predicted_age.tsv")
        df.to_csv(out_file, sep="\t", index=False)
        print("Finished. Group table created for %s" % " ".join(subjects_to_analyze))