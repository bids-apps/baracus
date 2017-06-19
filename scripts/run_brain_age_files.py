#! /usr/bin/env python
import os
import argparse
from pkg_resources import resource_filename, Requirement
from baracus.predict import predict_brain_age_single_subject
from baracus import models_list, __version__

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='BARACUS: Brain-Age Regression Analysis and Computation Utility Software. Files mode. '
                                                 'You specify lh/rh thickness/area + aseg file (with '
                                                 '--lh_thickness_file...). Surface files need to be sampled to '
                                                 'fsaverage4 space, aseg files extracted via asegstats2table. Only '
                                                 'one subject can be specified at a time.')
    parser.add_argument('out_dir', help='Results are put here.')
    parser.add_argument('--participant_label', help='will be written into output files and can be omitted')
    parser.add_argument('--models', choices=models_list, default=["Liem2016__OCI_norm"], help='',
                        nargs="+")
    parser.add_argument('--lh_thickness_file', required=True, help='')
    parser.add_argument('--rh_thickness_file', required=True, help='')
    parser.add_argument('--lh_area_file', required=True, help='')
    parser.add_argument('--rh_area_file', required=True, help='')
    parser.add_argument('--aseg_file', required=True, help='')
    parser.add_argument('-v', '--version', action='version',
                        version='BARACUS version {}'.format(__version__))

    args = parser.parse_args()

    model_dir = resource_filename(Requirement.parse("baracus"), 'models')

    if args.participant_label:
        subject = args.participant_label
    else:
        subject = ""
    predict_brain_age_single_subject(out_dir=args.out_dir,
                                     lh_thickness_file=args.lh_thickness_file,
                                     rh_thickness_file=args.rh_thickness_file,
                                     lh_area_file=args.lh_area_file,
                                     rh_area_file=args.rh_area_file,
                                     aseg_file=args.aseg_file,
                                     model_dir=model_dir,
                                     models=args.models,
                                     subject_label=subject)
