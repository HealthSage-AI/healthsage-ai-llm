import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.note_to_fhir.evaluation.datamodels import FhirDiff  # noqa: E402
from src.note_to_fhir.evaluation.utils import calculate_diff  # noqa: E402
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
    diff = calculate_diff(fhir_true, fhir_pred, "Bundle")
    return diff


def test_processing():
    diff = test_fhirdiff()

    assert (
        diff.score.n_leaves
        == diff.score.n_matches
        + diff.score.n_additions
        + diff.score.n_deletions
        + diff.score.n_modifications
    )
    assert diff.score.accuracy >= 0.0 and diff.score.accuracy <= 1.0


if __name__ == "__main__":
    test_processing()
