#! /usr/bin/env python

import argparse
import os

import pandas as pd
from bids.grabbids import BIDSLayout
from pkg_resources import resource_filename, Requirement

from baracus import models_list, __version__
from baracus.predict import predict_brain_age_single_subject
from baracus.prepare import run_prepare_all
from baracus.utils import run, get_subjects_session

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='BARACUS: Brain-Age Regression Analysis and Computation Utility Software. BIDS mode. '
                    'You specify a BIDS-formatted freesurfer folder as input. All data '
                    'is extracted automatiacally from that folder. ')
    parser.add_argument('bids_dir', help='The directory with the input dataset '
                                         'formatted according to the BIDS standard.')
    parser.add_argument('out_dir', help='Results are put into {out_dir}/baracus.')
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
    parser.add_argument('--freesurfer_dir', help="Folder with FreeSurfer subjects formatted according "
                                                 "to BIDS standard. If subject's recon-all folder "
                                                 "cannot be found, recon-all will be run. "
                                                 "If not specified freesurfer data will be saved to {"
                                                 "out_dir}/freesurfer")
    parser.add_argument('--models', choices=models_list, default=["Liem2016__OCI_norm"], help='',
                        nargs="+")
    parser.add_argument('--skip_missing', help='Flag to skip not segmented subjects', action='store_true')
    parser.add_argument('--license_key',
                        help='FreeSurfer license key - letters and numbers after "*" in the email you '
                             'received after registration. To register (for free) visit '
                             'https://surfer.nmr.mgh.harvard.edu/registration.html',
                        required=True)
    parser.add_argument('--n_cpus', help='Number of CPUs/cores available to use.', default=1, type=int)
    parser.add_argument('-v', '--version', action='version',
                        version='BARACUS version {}'.format(__version__))
    args = parser.parse_args()

    # set up output dirs
    if args.freesurfer_dir:
        freesurfer_dir = args.freesurfer_dir
    else:
        freesurfer_dir = os.path.join(args.out_dir, "freesurfer")
    out_dir = os.path.join(args.out_dir, "baracus")
    if not os.path.isdir(freesurfer_dir):
        os.makedirs(freesurfer_dir)
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)

    model_dir = resource_filename(Requirement.parse("baracus"), 'models')

    run("bids-validator " + args.bids_dir)
    layout = BIDSLayout(args.bids_dir)

    truly_longitudinal_study = True if len(layout.get_sessions()) > 1 else False
    subjects_to_analyze, sessions_to_analyze, freesurfer_subjects_to_analyze = get_subjects_session(layout,
                                                                                                    args.participant_label,
                                                                                                    truly_longitudinal_study)

    if args.analysis_level == "participant":

        data_files = run_prepare_all(args.bids_dir, freesurfer_dir, out_dir, subjects_to_analyze,
                                     sessions_to_analyze, args.n_cpus, args.license_key, args.skip_missing)

        for subject, d in data_files.items():
            d["out_dir"] = out_dir
            d["model_dir"] = model_dir
            d["models"] = args.models
            d["subject_label"] = subject
            predict_brain_age_single_subject(**d)

    elif args.analysis_level == "group":
        print("Creating group table...")
        df = pd.DataFrame([])
        for subject in freesurfer_subjects_to_analyze:
            in_file = os.path.join(out_dir, subject, subject + "_predicted_age.tsv")
            if os.path.isfile(in_file):
                df = df.append(pd.read_csv(in_file, sep="\t"))

        group_out_dir = os.path.join(out_dir, "00_group")
        if not os.path.isdir(group_out_dir):
            os.makedirs(group_out_dir)
        out_file = os.path.join(group_out_dir, "group_predicted_age.tsv")
        df.to_csv(out_file, sep="\t", index=False)
        print("Finished. Group table created for %s" % " ".join(subjects_to_analyze))
