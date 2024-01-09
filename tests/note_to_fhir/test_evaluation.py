import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.note_to_fhir.evaluation.datamodels import FhirDiff, FhirScore, ElementDetails
from src.note_to_fhir.evaluation.utils import calculate_diff
from src.note_to_fhir.evaluation.visuals import show_diff
from datasets import load_dataset
import json

testset = load_dataset("healthsage/example_fhir_output")


def test_fhirdiff() -> FhirDiff:
    """Tests the FhirDiff class

    Returns:
        FhirDiff: FhirDiff object (without score calculated)
    """
    fhir_pred = json.loads(testset['train']['note_to_fhir'][0])
    fhir_true = json.loads(testset['train']['fhir_true'][0])
    diff = FhirDiff(fhir_true=fhir_true, fhir_pred=fhir_pred, resource_name="Bundle")
    diff = calculate_diff(diff)
    return diff

def test_visualization():
    diff = test_fhirdiff()
    show_diff(diff)

def test_processing():
    diff = test_fhirdiff()
    
    assert diff.score.n_leaves == diff.score.n_matches + diff.score.n_additions + diff.score.n_deletions + diff.score.n_modifications
    assert diff.score.score >= 0.0 and diff.score.score <= 1.0


if __name__ == "__main__":
    test_processing()
    test_visualization()

    


