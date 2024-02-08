import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from src.note_to_fhir.data_utils import drop_snomed_loinc

sample = """{'resourceType': 'Bundle',
  'id': '1',
  'type': 'collection',
  'entry': [{'resource': {'resourceType': 'Encounter',
     'id': '1',
     'status': 'unknown',
     'class': {'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
      'code': 'AMB'},
     'subject': {'reference': 'Patient/1',
      'display': 'Mrs. Wonda Jasmin Abshire'}}},
   {'resource': {'resourceType': 'Encounter',
     'id': '2',
     'status': 'finished',
     'class': {'system': 'http://terminology.hl7.org/CodeSystem/v3-ActCode',
      'code': 'AMB'},
     'type': [{'coding': [{'system': 'http://snomed.info/sct',
         'code': '162673000',
         'display': 'General examination of patient (procedure)'}],
       'text': 'General examination of patient (procedure)'}],
     'subject': {'reference': 'Patient/1',
      'display': 'Mrs. Wonda Jasmin Abshire'},
     'participant': [{'type': [{'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v3-ParticipationType',
           'code': 'PPRF',
           'display': 'primary performer'}],
         'text': 'primary performer'}],
       'period': {'start': '2021-01-24T16:25:55+01:00',
        'end': '2021-01-24T17:23:15+01:00'},
       'individual': {'reference': 'Practitioner/1',
        'display': 'Dr. Clora Pagac'}}],
     'serviceProvider': {'reference': 'Organization/2',
      'display': 'MEASURED WELLNESS LLC'}}},
   {'resource': {'resourceType': 'Patient',
     'id': '1',
     'name': [{'use': 'official',
       'family': 'Abshire',
       'given': ['Wonda', 'Jasmin'],
       'prefix': ['Mrs.']},
      {'use': 'maiden',
       'family': 'Crona',
       'given': ['Wonda', 'Jasmin'],
       'prefix': ['Mrs.']}],
     'gender': 'female',
     'birthDate': '1963-12-15',
     'address': [{'line': ['391 Russel Stravenue Apt 17'],
       'city': 'Boston',
       'state': 'Massachusetts',
       'postalCode': '02132',
       'country': 'US'}],
     'maritalStatus': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/v3-MaritalStatus',
        'code': 'M',
        'display': 'Married'}],
      'text': 'Married'}}},
   {'resource': {'resourceType': 'Immunization',
     'id': '1',
     'status': 'unknown',
     'vaccineCode': {'coding': [{'system': 'http://hl7.org/fhir/sid/cvx',
        'code': '140',
        'display': 'Influenza, seasonal, injectable, preservative free'}],
      'text': 'Influenza, seasonal, injectable, preservative free'},
     'patient': {'reference': 'Patient/1'},
     'encounter': {'reference': 'Encounter/2'},
     'occurrenceDateTime': '2021-01-24T16:25:55+01:00'}},
   {'resource': {'resourceType': 'Practitioner',
     'id': '2',
     'telecom': [{'system': 'email',
       'value': "Iva908.O'Keefe54@example.com",
       'use': 'work'}]}},
   {'resource': {'resourceType': 'Practitioner',
     'id': '1',
     'gender': 'female'}},
   {'resource': {'resourceType': 'Observation',
     'id': '2',
     'status': 'unknown',
     'code': {'coding': [{'system': 'http://loinc.org',
        'code': '21000-5',
        'display': 'Erythrocyte distribution width [Entitic volume] by Automated count'}],
      'text': 'Erythrocyte distribution width [Entitic volume] by Automated count'},
     'subject': {'reference': 'Patient/1'},
     'encounter': {'reference': 'Encounter/2'},
     'valueQuantity': {'value': 44.012,
      'unit': 'fL',
      'system': 'http://unitsofmeasure.org',
      'code': 'fL'}}},
   {'resource': {'resourceType': 'Observation',
     'id': '1',
     'status': 'unknown',
     'code': {'coding': [{'system': 'http://loinc.org',
        'code': '4548-4',
        'display': 'Hemoglobin A1c/Hemoglobin.total in Blood'}],
      'text': 'Hemoglobin A1c/Hemoglobin.total in Blood'},
     'subject': {'reference': 'Patient/1'},
     'encounter': {'reference': 'Encounter/2'}}}]}
"""

fhir = eval(sample)
fhir_clean = drop_snomed_loinc(fhir)
assert "snomed" not in json.dumps(fhir_clean)
