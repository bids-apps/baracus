import os
import numpy as np
import nibabel as nb
import pandas as pd
import pickle
from collections import OrderedDict
import baracus


def _vectorize_fs_surf(in_data_file):
    img = nb.load(in_data_file)
    in_data = img.get_data().squeeze()
    vectorized_data = in_data[np.newaxis, ...]
    assert vectorized_data.shape == (1, 2562), "%s shape does not look right: %s" % (in_data_file,
                                                                                     vectorized_data.shape)

    return vectorized_data


def _vectorize_fs_tab(in_data_file):
    df = pd.read_csv(in_data_file, index_col=0, delimiter='\t')
    vectorized_data = df.values
    assert vectorized_data.shape == (1, 66), "%s shape does not look right: %s" % (in_data_file,
                                                                                   vectorized_data.shape)
    return vectorized_data


def combine_surfs(lh_file, rh_file):
    lh_data = _vectorize_fs_surf(lh_file)
    rh_data = _vectorize_fs_surf(rh_file)
    return np.concatenate((lh_data, rh_data), 1)


def load_model(model_file):
    try:
        with open(model_file, 'r') as f:
            pipe = pickle.load(f)
    except:
        # load python 2 pickles with python 3
        # http://stackoverflow.com/questions/28218466/unpickling-a-python-2-object-with-python-3
        with open(model_file, 'rb') as f:
            pipe = pickle.load(f, encoding='latin1')
    return pipe


def get_models(model_dir, model):
    modalities = ["aseg", "area", "thickness", "fs"]
    models = {}
    for m in modalities:
        model_file = os.path.join(model_dir, model, "{m}/trained_model.pkl".format(m=m))
        models[m] = load_model(model_file)
    models["model_name"] = model
    return models


def get_data(lh_thickness_file, rh_thickness_file, lh_area_file, rh_area_file, aseg_file):
    X = {}
    X["thickness"] = combine_surfs(lh_thickness_file, rh_thickness_file)
    X["area"] = combine_surfs(lh_area_file, rh_area_file)
    X["aseg"] = _vectorize_fs_tab(aseg_file)
    return (X)


# https://github.com/fliem/LeiCA_LIFE/blob/e9d02464a9e43b97cef9c7b753d88120cfbd6c94/learning/learning_utils.py#L691
def predict_from_model(X, model):
    y_predicted = model.predict(X)
    return y_predicted


def predict_brain_age(X, models, subject_label=""):
    df = pd.DataFrame([])
    y_predicted = {}

    # SINGLE MODALITY
    for m in ["aseg", "area", "thickness"]:
        y_predicted[m] = predict_from_model(X[m], models[m])
        d = OrderedDict([
            ("subject_id", subject_label), ("model", models["model_name"]),
            ("modality", m), ("predicted_age", y_predicted[m]), ("baracus_version", baracus.__version__)])
        df = df.append(pd.DataFrame(d))

    # MULTI MODAL
    y_stacked = []
    for m in ["aseg", "area", "thickness"]:
        y_stacked.append(y_predicted[m][0])

    m = "fs"
    out_modality = "stacked-anatomy"

    X[m] = np.atleast_2d(y_stacked)
    y_predicted[m] = predict_from_model(X[m], models[m])
    d = OrderedDict([
        ("subject_id", subject_label), ("model", models["model_name"]),
        ("modality", out_modality), ("predicted_age", y_predicted[m]), ("baracus_version", baracus.__version__)])
    df = df.append(pd.DataFrame(d))

    return df


def predict_brain_age_single_subject(out_dir, lh_thickness_file, rh_thickness_file, lh_area_file, rh_area_file,
                                     aseg_file, model_dir, models=["Liem2016__OCI_norm"], subject_label=""):
    X = get_data(lh_thickness_file, rh_thickness_file, lh_area_file, rh_area_file, aseg_file)

    df = pd.DataFrame([])

    for ba_model in models:
        fitted_models = get_models(model_dir, model=ba_model)

        df_ = predict_brain_age(X, fitted_models, subject_label=subject_label)
        df = df.append(df_)

    subject_dir = os.path.join(out_dir, subject_label)
    if not os.path.isdir(subject_dir):
        os.makedirs(subject_dir)
    if subject_label:
        subject_str = subject_label + "_"
    else:
        subject_str = ""
    out_file = os.path.join(subject_dir, subject_str + "predicted_age.tsv")
    df.to_csv(out_file, sep="\t", index=False)
    print("FINISHED. Predicted and saved %s %s" % (subject_label, out_file))
