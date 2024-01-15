import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.note_to_fhir.evaluation.utils import calculate_diff  # noqa: E402
from src.note_to_fhir.evaluation.visuals import show_diff  # noqa: E402
from datasets import load_dataset  # noqa: E402

testset = load_dataset("healthsage/example_fhir_output")


def run_diff_visualization():
    fhir_pred = json.loads(testset["train"]["note_to_fhir"][0])
    fhir_true = json.loads(testset["train"]["fhir_true"][0])
    diff = calculate_diff(fhir_true, fhir_pred, "Bundle")
    show_diff(diff)


if __name__ == "__main__":
    run_diff_visualization()
