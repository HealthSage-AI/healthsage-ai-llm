from healthsageai.note_to_fhir.evaluation.datamodels import FhirDiff  # noqa: E402
from healthsageai.note_to_fhir.evaluation.utils import (
    get_diff,
    diff_to_list,
    diff_to_dataframe,
)  # noqa: E402
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


def test_fhirdiff_edge_case() -> FhirDiff:
    fhir_true = {
        "resourceType": "Procedure",
        "id": "1",
        "status": "unknown",
        "code": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "display": "History AND physical examination (procedure)",
                }
            ],
            "text": "History AND physical examination (procedure)",
        },
        "subject": {"reference": "Patient/1"},
        "performedPeriod": None,
    }
    fhir_pred = {
        "resourceType": "Observation",
        "id": "1",
        "status": "final",
        "category": [
            {
                "coding": [
                    {
                        "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                        "code": "vital-signs",
                        "display": "Vital signs",
                    }
                ]
            }
        ],
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "display": "Body mass index (BMI) [Ratio]",
                }
            ],
            "text": "Body mass index (BMI) [Ratio]",
        },
        "subject": {"reference": "Patient/1"},
        "effectiveDateTime": "2021-06-06T19:50:28+02:00",
        "issued": None,
        "valueQuantity": {
            "value": 30.7,
            "unit": "kg/m2",
            "system": "http://unitsofmeasure.org",
            "code": "kg/m2",
        },
    }
    get_diff(fhir_true, fhir_pred, resource_type="Procedure")


def test_fhirdiff_edge_case_2() -> FhirDiff:
    fhir_pred = {
        "resourceType": "Bundle",
        "id": "1",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "1",
                    "name": [
                        {
                            "use": "official",
                            "family": "Cruickshank",
                            "given": ["Jordon", "Elbert"],
                            "prefix": ["Mr."],
                        }
                    ],
                    "telecom": [
                        {"system": "phone", "value": "555-505-9461", "use": "home"}
                    ],
                    "gender": "male",
                    "multipleBirthBoolean": False,
                }
            },
            {
                "resource": {
                    "resourceType": "Procedure",
                    "id": "3",
                    "status": "unknown",
                    "subject": {"reference": "Patient/1"},
                }
            },
            {
                "resource": {
                    "resourceType": "Procedure",
                    "id": "2",
                    "status": "unknown",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "Electrocardiographic procedure (procedure)",
                            }
                        ],
                        "text": "Electrocardiographic procedure (procedure)",
                    },
                    "subject": {"reference": "Patient/1"},
                }
            },
            {
                "resource": {
                    "resourceType": "Procedure",
                    "id": "1",
                    "status": "unknown",
                    "subject": {"reference": "Patient/1"},
                }
            },
            {
                "resource": {
                    "resourceType": "Procedure",
                    "id": "4",
                    "status": "unknown",
                    "subject": {"reference": "Patient/1"},
                }
            },
        ],
    }

    fhir_true = {
        "resourceType": "Bundle",
        "id": "1",
        "type": "collection",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "1",
                    "name": [
                        {
                            "use": "official",
                            "family": "Cruickshank",
                            "given": ["Jordon", "Elbert"],
                            "prefix": ["Mr."],
                        }
                    ],
                    "telecom": [
                        {"system": "phone", "value": "555-505-9461", "use": "home"}
                    ],
                    "gender": "male",
                    "multipleBirthBoolean": False,
                }
            },
            {
                "resource": {
                    "resourceType": "Procedure",
                    "id": "1",
                    "status": "unknown",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "Electrocardiogram (procedure)",
                            }
                        ],
                        "text": "Electrocardiogram (procedure)",
                    },
                    "subject": {"reference": "Patient/1"},
                }
            },
            None,
            None,
            None,
        ],
    }

    diff = get_diff(fhir_true, fhir_pred, resource_type="Bundle")
    assert diff.score.accuracy >= 0 and diff.score.accuracy <= 1.0


def test_edge_case_3():
    fhir_true = {
        "resourceType": "Bundle",
        "id": "1",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "1",
                    "name": [
                        {
                            "use": "official",
                            "family": "Vink",
                            "given": ["Jinthe"],
                            "prefix": ["Mevr."],
                        }
                    ],
                    "gender": "female",
                    "birthDate": "1995-06-04",
                    "address": [
                        {
                            "line": ["Janspoort 2 X"],
                            "city": "Arnhem",
                            "state": "Gelderland",
                            "postalCode": "6811GE",
                            "country": "NL",
                        }
                    ],
                    "multipleBirthBoolean": False,
                }
            },
            {
                "resource": {
                    "resourceType": "Practitioner",
                    "id": "1",
                    "name": [
                        {"family": "Coenen", "given": ["Esila"], "prefix": ["Dr."]}
                    ],
                    "telecom": [
                        {
                            "system": "email",
                            "value": "esilacoe@yahoo.net",
                            "use": "work",
                        }
                    ],
                    "address": [
                        {
                            "line": ["Faustlaan 4 VIII"],
                            "city": "Nieuwegein",
                            "state": "Utrecht",
                            "postalCode": "3438ES",
                            "country": "NL",
                        }
                    ],
                    "gender": "female",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "12",
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2012-07-22T05:47:49+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "14",
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2019-05-12T06:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "5",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "pre-eclampsie (aandoening)",
                            }
                        ],
                        "text": "pre-eclampsie (aandoening)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "2",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "normale zwangerschap (bevinding)",
                            }
                        ],
                        "text": "normale zwangerschap (bevinding)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2017-08-13T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "1",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "normale zwangerschap (bevinding)",
                            }
                        ],
                        "text": "normale zwangerschap (bevinding)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2020-07-26T04:13:36+02:00",
                    "abatementDateTime": "2021-02-21T03:13:36+01:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "4",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active",
                            }
                        ]
                    },
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "3",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2017-12-25T03:59:56+01:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "13",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "Received certificate of high school equivalency (finding)",
                            }
                        ],
                        "text": "Received certificate of high school equivalency (finding)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2013-07-28T05:10:02+02:00",
                    "recordedDate": "2013-07-28T05:10:02+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "9",
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2017-08-06T04:13:36+02:00",
                    "abatementDateTime": "2023-08-13T04:13:36+02:00",
                    "recordedDate": "2017-08-06T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "6",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "code": {
                        "coding": [
                            {"system": "http://snomed.info/sct", "display": "stress"}
                        ],
                        "text": "stress",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2017-08-06T05:06:29+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "7",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active",
                            }
                        ]
                    },
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2017-08-06T05:06:29+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "11",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "abatementDateTime": "2014-08-03T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "8",
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2023-07-02T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "10",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "resolved",
                            }
                        ]
                    },
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "commotio cerebri (aandoening)",
                            }
                        ],
                        "text": "commotio cerebri (aandoening)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "3",
                    "status": "finished",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                    },
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "display": "consultatie voor behandeling",
                                }
                            ],
                            "text": "consultatie voor behandeling",
                        }
                    ],
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "participant": [
                        {
                            "type": [
                                {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                            "code": "PPRF",
                                            "display": "primary performer",
                                        }
                                    ],
                                    "text": "primary performer",
                                }
                            ],
                            "period": {
                                "start": "2016-04-27T04:13:36+02:00",
                                "end": "2016-04-27T04:28:36+02:00",
                            },
                            "individual": {
                                "reference": "Practitioner/1",
                                "display": "Dr. Esila Coenen",
                            },
                        }
                    ],
                    "period": {
                        "start": "2016-04-27T04:13:36+02:00",
                        "end": "2016-04-27T04:28:36+02:00",
                    },
                    "serviceProvider": {
                        "reference": "Organization/1",
                        "display": "Amsterdam Ziekenhuis",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "1",
                    "status": "unknown",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "participant": [
                        {
                            "type": [
                                {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                            "code": "PPRF",
                                            "display": "primary performer",
                                        }
                                    ],
                                    "text": "primary performer",
                                }
                            ],
                            "period": {
                                "start": "2018-03-11T03:13:36+01:00",
                                "end": "2018-03-11T03:28:36+01:00",
                            },
                            "individual": {
                                "reference": "Practitioner/1",
                                "display": "Dr. Esila Coenen",
                            },
                        }
                    ],
                    "reasonCode": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "display": "normale zwangerschap (bevinding)",
                                }
                            ]
                        }
                    ],
                    "serviceProvider": {
                        "reference": "Organization/1",
                        "display": "Amsterdam Ziekenhuis",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "2",
                    "status": "finished",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "participant": [
                        {
                            "period": {
                                "start": "2021-04-04T04:13:36+02:00",
                                "end": "2021-04-04T04:28:36+02:00",
                            },
                            "individual": {
                                "reference": "Practitioner/1",
                                "display": "Dr. Esila Coenen",
                            },
                        }
                    ],
                    "serviceProvider": {
                        "reference": "Organization/1",
                        "display": "Amsterdam Ziekenhuis",
                    },
                }
            },
            None,
            None,
        ],
    }

    fhir_pred = {
        "resourceType": "Bundle",
        "id": "1",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "1",
                    "name": [
                        {
                            "use": "official",
                            "family": "Vink",
                            "given": ["Jinthe"],
                            "prefix": ["Mevr."],
                        }
                    ],
                    "gender": "female",
                    "birthDate": "1995-06-04",
                    "address": [
                        {
                            "line": ["Janspoort 2 X"],
                            "city": "Arnhem",
                            "state": "Gelderland",
                            "postalCode": "6811GE",
                            "country": "NL",
                        }
                    ],
                    "multipleBirthBoolean": False,
                }
            },
            {
                "resource": {
                    "resourceType": "Practitioner",
                    "id": "1",
                    "name": [
                        {"family": "Coenen", "given": ["Esila"], "prefix": ["Dr."]}
                    ],
                    "telecom": [
                        {
                            "system": "email",
                            "value": "esilacoe@yahoo.net",
                            "use": "work",
                        }
                    ],
                    "address": [
                        {
                            "line": ["Faustlaan 4 VIII"],
                            "city": "Nieuwegein",
                            "state": "Utrecht",
                            "postalCode": "3438ES",
                            "country": "NL",
                        }
                    ],
                    "gender": "female",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "1",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "medicatieverificatie (verrichting)",
                            }
                        ],
                        "text": "medicatieverificatie (verrichting)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2013-07-28T05:10:02+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "14",
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2019-05-12T06:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "12",
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2012-07-22T05:47:49+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "11",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "abatementDateTime": "2014-08-03T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "10",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "resolved",
                            }
                        ]
                    },
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "pre-eclampsie (aandoening)",
                            }
                        ],
                        "text": "pre-eclampsie (aandoening)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "13",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "bevinding betreffende certificaat of opleiding (bevinding)",
                            }
                        ],
                        "text": "bevinding betreffende certificaat of opleiding (bevinding)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "3",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active",
                            }
                        ]
                    },
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2017-08-06T05:06:29+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "4",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active",
                            }
                        ]
                    },
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "5",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "code": {
                        "coding": [
                            {"system": "http://snomed.info/sct", "display": "stress"}
                        ],
                        "text": "stress",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2017-08-06T05:06:29+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "2",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "normale zwangerschap (bevinding)",
                            }
                        ],
                        "text": "normale zwangerschap (bevinding)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2020-07-26T04:13:36+02:00",
                    "abatementDateTime": "2021-02-21T03:13:36+01:00",
                    "recordedDate": "2020-07-26T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "9",
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "onsetDateTime": "2017-08-06T04:13:36+02:00",
                    "abatementDateTime": "2023-08-13T04:13:36+02:00",
                    "recordedDate": "2017-08-06T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "7",
                    "clinicalStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                                "code": "active",
                            }
                        ]
                    },
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2017-08-06T05:06:29+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "8",
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "recordedDate": "2023-07-02T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "1",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "abatementDateTime": "2014-08-03T04:13:36+02:00",
                    "recordedDate": "2014-08-03T04:13:36+02:00",
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "6",
                    "verificationStatus": {
                        "coding": [
                            {
                                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                                "code": "confirmed",
                            }
                        ]
                    },
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "medicatieverificatie (verrichting)",
                            }
                        ],
                        "text": "medicatieverificatie (verrichting)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "15",
                    "code": {
                        "coding": [
                            {
                                "system": "http://snomed.info/sct",
                                "display": "medicatieverificatie (verrichting)",
                            }
                        ],
                        "text": "medicatieverificatie (verrichting)",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "3",
                    "status": "finished",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                    },
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "display": "contact vanwege probleem (verrichting)",
                                }
                            ],
                            "text": "contact vanwege probleem (verrichting)",
                        }
                    ],
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "participant": [
                        {
                            "type": [
                                {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                            "code": "PPRF",
                                            "display": "primary performer",
                                        }
                                    ],
                                    "text": "primary performer",
                                }
                            ],
                            "period": {
                                "start": "2016-04-27T04:13:36+02:00",
                                "end": "2016-04-27T04:28:36+02:00",
                            },
                            "individual": {
                                "reference": "Practitioner/1",
                                "display": "Dr. Esila Coenen",
                            },
                        }
                    ],
                    "period": {
                        "start": "2016-04-27T04:13:36+02:00",
                        "end": "2016-04-27T04:28:36+02:00",
                    },
                    "serviceProvider": {
                        "reference": "Organization/1",
                        "display": "Amsterdam Ziekenhuis",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "1",
                    "status": "finished",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "participant": [
                        {
                            "type": [
                                {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                            "code": "PPRF",
                                            "display": "primary performer",
                                        }
                                    ],
                                    "text": "primary performer",
                                }
                            ],
                            "period": {
                                "start": "2021-04-04T04:13:36+02:00",
                                "end": "2021-04-04T04:28:36+02:00",
                            },
                            "individual": {
                                "reference": "Practitioner/1",
                                "display": "Dr. Esila Coenen",
                            },
                        }
                    ],
                    "period": {
                        "start": "2021-04-04T04:13:36+02:00",
                        "end": "2021-04-04T04:28:36+02:00",
                    },
                    "serviceProvider": {
                        "reference": "Organization/1",
                        "display": "Amsterdam Ziekenhuis",
                    },
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "2",
                    "status": "finished",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                    },
                    "type": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "display": "contact vanwege probleem (verrichting)",
                                }
                            ],
                            "text": "contact vanwege probleem (verrichting)",
                        }
                    ],
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mevr. Jinthe Vink",
                    },
                    "participant": [
                        {
                            "type": [
                                {
                                    "coding": [
                                        {
                                            "system": "http://terminology.hl7.org/CodeSystem/v3-ParticipationType",
                                            "code": "PPRF",
                                            "display": "primary performer",
                                        }
                                    ],
                                    "text": "primary performer",
                                }
                            ],
                            "period": {
                                "start": "2018-03-11T03:13:36+01:00",
                                "end": "2018-03-11T03:28:36+01:00",
                            },
                            "individual": {
                                "reference": "Practitioner/1",
                                "display": "Dr. Esila Coenen",
                            },
                        }
                    ],
                    "period": {
                        "start": "2018-03-11T03:13:36+01:00",
                        "end": "2018-03-11T03:28:36+01:00",
                    },
                    "reasonCode": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "display": "normale zwangerschap (bevinding)",
                                }
                            ]
                        }
                    ],
                    "serviceProvider": {
                        "reference": "Organization/1",
                        "display": "Amsterdam Ziekenhuis",
                    },
                }
            },
        ],
    }

    diff = get_diff(fhir_true, fhir_pred, resource_type="Bundle")
    assert diff.score.accuracy >= 0 and diff.score.accuracy <= 1.0


def test_edge_case_4():
    fhir_pred = {
        "resourceType": "Bundle",
        "id": "1",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "1",
                    "name": [
                        {
                            "use": "official",
                            "family": "Auer",
                            "given": ["Layla", "Mariko"],
                            "prefix": ["Mrs."],
                            "suffix": ["PhD"],
                        }
                    ],
                    "telecom": [
                        {"system": "phone", "value": "555-350-8694", "use": "home"}
                    ],
                    "address": [
                        {
                            "line": ["549 Dare Pathway Unit 28"],
                            "city": "Medway",
                            "state": "Massachusetts",
                            "postalCode": "00000",
                        }
                    ],
                }
            },
            {
                "resource": {
                    "resourceType": "Practitioner",
                    "id": "1",
                    "name": [
                        {
                            "family": "Schumm",
                            "given": ["Nickolas", None],
                            "prefix": ["Dr."],
                        }
                    ],
                    "address": [
                        {
                            "line": ["250 POND STREET"],
                            "city": "FRAMINGHAM",
                            "state": "MA",
                            "postalCode": "017014592",
                            "country": "US",
                        }
                    ],
                    "gender": "male",
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "1",
                    "status": "unknown",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mrs. Layla Mariko Auer",
                    },
                    "participant": [
                        {
                            "individual": {
                                "reference": "Practitioner/1",
                                "display": "Dr. Nickolas Schumm",
                            }
                        }
                    ],
                    "period": {
                        "start": "2015-02-04T17:30:00+01:00",
                        "end": "2015-02-04T17:45:00+01:00",
                    },
                    "reasonCode": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "display": "Normal pregnancy",
                                }
                            ]
                        }
                    ],
                    "serviceProvider": {
                        "reference": "Organization/1",
                        "display": "ENCOMPASS HEALTH BRAINTREE HOSPITAL OF BRAINTREE",
                    },
                }
            },
        ],
    }
    fhir_true = {
        "resourceType": "Bundle",
        "id": "1",
        "type": "transaction",
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "1",
                    "name": [
                        {
                            "use": "official",
                            "family": "Auer",
                            "given": ["Layla", "Mariko"],
                            "prefix": ["Mrs."],
                            "suffix": ["PhD"],
                        }
                    ],
                    "telecom": [
                        {"system": "phone", "value": "555-350-8694", "use": "home"}
                    ],
                    "address": [
                        {
                            "line": ["549 Dare Pathway Unit 28"],
                            "city": "Medway",
                            "state": "Massachusetts",
                            "postalCode": "00000",
                        }
                    ],
                }
            },
            {
                "resource": {
                    "resourceType": "Practitioner",
                    "id": "1",
                    "name": [
                        {
                            "family": "Schumm",
                            "given": ["Nickolas", None],
                            "prefix": ["Dr."],
                        }
                    ],
                    "address": [
                        {
                            "line": ["250 POND STREET"],
                            "city": "FRAMINGHAM",
                            "state": "MA",
                            "postalCode": "017014592",
                            "country": "US",
                        }
                    ],
                    "gender": "male",
                }
            },
            {
                "resource": {
                    "resourceType": "Encounter",
                    "id": "1",
                    "status": "unknown",
                    "class": {
                        "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                        "code": "AMB",
                    },
                    "subject": {
                        "reference": "Patient/1",
                        "display": "Mrs. Layla Mariko Auer",
                    },
                    "participant": [
                        {
                            "individual": {
                                "reference": "Practitioner/1",
                                "display": "Dr. Nickolas Schumm",
                            }
                        }
                    ],
                    "period": {
                        "start": "2015-02-04T17:30:31+01:00",
                        "end": "2015-02-04T17:45:31+01:00",
                    },
                    "reasonCode": [
                        {
                            "coding": [
                                {
                                    "system": "http://snomed.info/sct",
                                    "display": "Normal pregnancy",
                                }
                            ]
                        }
                    ],
                    "serviceProvider": {
                        "reference": "Organization/1",
                        "display": "ENCOMPASS HEALTH BRAINTREE HOSPITAL OF BRAINTREE",
                    },
                }
            },
        ],
    }
    diff = get_diff(fhir_true, fhir_pred, resource_type="Bundle")

    assert diff.score.accuracy >= 0 and diff.score.accuracy <= 1.0


def test_diff_to_list():
    diff = test_fhirdiff()
    diff_list = diff_to_list(diff)
    assert len(diff_list) >= diff.score.n_leaves


def test_diff_to_dataframe():
    diff = test_fhirdiff()
    diff_df = diff_to_dataframe(diff)
    assert len(diff_df) >= diff.score.n_leaves


if __name__ == "__main__":
    test_edge_case_4()
    test_edge_case_3()
    test_fhirdiff_edge_case_2()
    test_fhirdiff_edge_case()
    test_fhirdiff()
    test_fhirdiff_encounter()
    test_diff_to_list()
    test_diff_to_dataframe()
