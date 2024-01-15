import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.note_to_fhir.evaluation.datamodels import FhirDiff  # noqa: E402
from src.note_to_fhir.evaluation.utils import get_diff, diff_to_list, diff_to_dataframe  # noqa: E402
from datasets import load_dataset  # noqa: E402
import json  # noqa: E402

testset = load_dataset("healthsage/example_fhir_output")


def test_fhirdiff() -> FhirDiff:
    """Tests the FhirDiff class

    Returns:
        FhirDiff: FhirDiff object (without score calculated)
    """
    fhir_pred = json.loads(testset["train"]["note_to_fhir"][0])
    fhir_true = json.loads(testset["train"]["fhir_true"][0])
    diff = get_diff(fhir_true, fhir_pred, "Bundle")
    assert (
        diff.score.n_leaves
        == diff.score.n_matches
        + diff.score.n_additions
        + diff.score.n_deletions
        + diff.score.n_modifications
    )
    assert diff.score.accuracy >= 0.0 and diff.score.accuracy <= 1.0
    return diff


def test_diff_to_list():
    diff = test_fhirdiff()
    diff_list = diff_to_list(diff)
    assert len(diff_list) >= diff.score.n_leaves

def test_diff_to_dataframe():
    diff = test_fhirdiff()
    diff_df = diff_to_dataframe(diff)
    assert len(diff_df) >= diff.score.n_leaves


    

if __name__ == "__main__":
    test_fhirdiff()
    test_diff_to_list()
    test_diff_to_dataframe()
