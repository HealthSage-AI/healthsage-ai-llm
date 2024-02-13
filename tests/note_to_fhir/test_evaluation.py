import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from healthsageai.note_to_fhir.evaluation.datamodels import FhirDiff  # noqa: E402
from healthsageai.note_to_fhir.evaluation.utils import get_diff, diff_to_list, diff_to_dataframe  # noqa: E402
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


def test_fhirdiff_encounter() -> FhirDiff:
    """Tests the FhirDiff class

    Returns:
        FhirDiff: FhirDiff object (without score calculated)
    """
    fhir_pred = json.loads(testset["train"]["note_to_fhir"][0])["entry"][0]
    fhir_true = json.loads(testset["train"]["fhir_true"][0])["entry"][0]
    diff = get_diff(fhir_true, fhir_pred, "BundleEntry")
    assert (
        diff.score.n_leaves
        == diff.score.n_matches
        + diff.score.n_additions
        + diff.score.n_deletions
        + diff.score.n_modifications
    )
    assert diff.score.accuracy > 0.0 and diff.score.accuracy < 1.0
    return diff

def test_fhirdiff_edge_case_1() -> FhirDiff:
    fhir_pred = {'resourceType': 'Observation',
            'id': '1',
            'status': 'final',
            'category': [{'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/observation-category',
                'code': 'vital-signs',
                'display': 'Vital signs'}]}],
            'code': {'coding': [{'system': 'http://loinc.org',
                'display': 'Body mass index (BMI) [Ratio]'}],
            'text': 'Body mass index (BMI) [Ratio]'},
            'subject': {'reference': 'Patient/1'},
            'effectiveDateTime': '2021-06-06T19:50:28+02:00',
            'issued': None,
            'valueQuantity': {'value': 30.7,
            'unit': 'kg/m2',
            'system': 'http://unitsofmeasure.org',
            'code': 'kg/m2'}}
    fhir_true = {'resourceType': 'Procedure',
            'id': '1',
            'status': 'unknown',
            'code': {'coding': [{'system': 'http://snomed.info/sct',
                'display': 'History AND physical examination (procedure)'}],
            'text': 'History AND physical examination (procedure)'},
            'subject': {'reference': 'Patient/1'},
            'performedPeriod': None}
    get_diff(fhir_true, fhir_pred, resource_type="Procedure")


def test_diff_to_list():
    diff = test_fhirdiff()
    diff_list = diff_to_list(diff)
    assert len(diff_list) >= diff.score.n_leaves


def test_diff_to_dataframe():
    diff = test_fhirdiff()
    diff_df = diff_to_dataframe(diff)
    assert len(diff_df) >= diff.score.n_leaves


if __name__ == "__main__":
    test_fhirdiff_edge_case_1()
    test_fhirdiff()
    test_fhirdiff_encounter()
    test_diff_to_list()
    test_diff_to_dataframe()
