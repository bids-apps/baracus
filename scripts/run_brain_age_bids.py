#! /usr/bin/env python

import argparse
import os
from glob import glob
import pandas as pd
from pkg_resources import resource_filename, Requirement
from bauto.predict import predict_brain_age_single_subject
from bauto.prepare import run_prepare_all

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BAuto: automatic prediction of Brain Age. BIDS mode. '
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
    parser.add_argument('--model', choices=["Liem2016__OCI_norm"], default="Liem2016__OCI_norm", help='')



    args = parser.parse_args()

    model_dir = resource_filename(Requirement.parse("bauto"), 'models')
    if args.participant_label:
        subjects_to_analyze = args.participant_label
    else:
        subject_dirs = glob(os.path.join(args.freesurfer_dir, "sub-*"))
        subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

    if args.analysis_level == "participant":
        data_files = run_prepare_all(args.freesurfer_dir, args.out_dir, subjects_to_analyze)

        for subject, d in data_files.items():
            d["out_dir"] = args.out_dir
            d["model_dir"] = model_dir
            d["model"] = args.model
            d["subject_label"] = "sub-" + subject
            predict_brain_age_single_subject(**d)

    elif args.analysis_level == "group":
        print("Creating group table...")
        df = pd.DataFrame([])
        for subject in subjects_to_analyze:
            in_file = os.path.join(args.out_dir, "sub-" + subject, "sub-" + subject + "_predicted_age.tsv")
            df = df.append(pd.read_csv(in_file, sep="\t"))

        group_out_dir = os.path.join(args.out_dir, "00_group")
        if not os.path.isdir(group_out_dir):
            os.makedirs(group_out_dir)
        out_file = os.path.join(group_out_dir, "group_predicted_age.tsv")
        df.to_csv(out_file, sep="\t", index=False)
        print("Finished. Group table created for %s" % " ".join(subjects_to_analyze))