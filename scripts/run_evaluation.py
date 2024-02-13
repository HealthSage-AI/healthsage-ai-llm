import json
import sys
import os
from healthsageai.note_to_fhir.evaluation.utils import get_diff, diff_to_dataframe  # noqa: E402
from datasets import load_dataset  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

testset = load_dataset("healthsageai/example_fhir_output")



def bar_chart_per_resource():
    """Generate a matplotlib bar chart of the accuracy per resource type
    """
    dfs = []
    for i in range(len(testset["train"]["note_to_fhir"])):
        fhir_pred = json.loads(testset["train"]["note_to_fhir"][i])
        fhir_true = json.loads(testset["train"]["fhir_true"][i])
        diff = get_diff(fhir_true, fhir_pred, "Bundle")
        df = diff_to_dataframe(diff)
        dfs.append(df)
    df = pd.concat(dfs, axis=0, ignore_index=True)
    df[["resource_type", "accuracy"]].groupby("resource_type").mean()["accuracy"].plot(
        kind="bar"
    )
    plt.show()


bar_chart_per_resource()