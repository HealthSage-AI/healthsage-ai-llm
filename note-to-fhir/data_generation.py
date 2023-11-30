#  Copyright (c) 2023. HealthSage AI.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import pandas as pd
import numpy as np
import time
from inference import get_openai_chatcompletion
from templates.simple import resource_to_note_template
import os
import json
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.practitioner import Practitioner
from fhir.resources.R4B.procedure import Procedure
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.allergyintolerance import AllergyIntolerance
from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.observation import Observation
from fhir.resources.R4B.bundle import Bundle
import copy


fhir_dataset = f"{os.path.expanduser('~')}/Downloads/output/fhir"
print(fhir_dataset)
custom_detail_options = {
    "custom_detail_1": ["abbreviate words", "make it look human with some typo's"],
    "custom_detail_2": ["write in list/bullet point style", "write staccato style","write in narrative style."],
    "custom_detail_3": ["use layman's language", "use medical jargon", "use very simple language"]
}

resource_mapping = {
    "Patient": Patient,
    "Condition": Condition,
    "Encounter": Encounter,
    "Organization": Organization,
    "Practitioner": Practitioner,
    "Procedure": Procedure,
    "AllergyIntolerance": AllergyIntolerance,
    "Immunization": Immunization,
    "Observation": Observation
}

OPENAI_MODEL = "gpt-4"


def convert_to_note(resource_bundle: dict, retries=5):
    if retries == 0 or len(resource_bundle['entry']) == 0:
        return ""
    custom_details = {
        k: np.random.choice(v) for k, v in custom_detail_options.items()
    }
    resource_bundle_sparse = copy.deepcopy(resource_bundle)
    entries_sparse = []
    for entry in resource_bundle_sparse['entry']:
        entry_resource = entry['resource']
        keyvalues = [(k, v) for k, v in entry_resource.items()]
        for k, v in keyvalues:
            if v is None:
                del entry_resource[k]
        entries_sparse.append(entry_resource)
    resource_bundle_sparse['entry'] = entries_sparse
    prompt = resource_to_note_template.format(
        resource=resource_bundle_sparse, **custom_details)
    messages = [
        {"role": "system", "content": "you are a program that converts structured data to natural language"},
        {"role": "user", "content": prompt}]
    
    try:
        response = get_openai_chatcompletion(messages, temperature=1.)
        note = response.to_dict()['choices'][0]['message']['content']
        case = np.random.choice(["same", "lower", "upper"], p=[0.9, 0.08, 0.02])
        if case == "lower":
            note = note.lower()
        elif case == "upper":
            note = note.upper()

        return note
    except:
        return ""


def read_bulk_resource(subfolder):

    filepath = os.path.join(fhir_dataset, subfolder)

    with open(filepath, 'r') as file:
        resources = file.readlines()

    for i in range(len(resources)):
        resources[i] = json.loads(resources[i])

    return resources


# V1
all_patients = read_bulk_resource("Patient.ndjson")
all_encounters = read_bulk_resource("Encounter.ndjson")
all_organizations = read_bulk_resource("Organization.ndjson")
all_practitioners = read_bulk_resource("Practitioner.ndjson")


# V2
all_allergyintolerance = read_bulk_resource("AllergyIntolerance.ndjson")
all_condition = read_bulk_resource("Condition.ndjson")
all_immunization = read_bulk_resource("Immunization.ndjson")
all_observation = read_bulk_resource("Observation.ndjson")
all_procedure = read_bulk_resource("Procedure.ndjson")


def drop_keys(resource):
    resourcetype = resource["resourceType"]
    resource_spec = resource_mapping[resourcetype]

    required_additions = ["resourceType", "id", "encounter", "subject", "patient"]

    # Select which keys could be technically dropped
    potential_keys_to_drop = [x.alias for x in resource_spec.element_properties() if x.required==False and x.name in resource.keys() and x.name not in required_additions]

    # Select which keys must be kept
    required_keys = [x.name for x in resource_spec.element_properties() if x.required==True or x.name in required_additions]
    required_keys = required_keys + [x.alias for x in resource_spec.element_properties() if x.required==True or x.alias in required_additions] + ["resourceType"]
    required_keys = set(required_keys)

    # Count number of keys in resource that should be kept
    n_required_keys_in_resource = len([x for x in required_keys if x in resource.keys()])

    # If there are no required keys in the resource, keep at least one optional key.
    # Avoid making a completely empty resource.
    save_keys = 1 if n_required_keys_in_resource == 0 else 0

    # Choose how many optional keys can be in the resource. 
    # At least two if there are no required keys (id + something else), otherwise one (just id). 
    # At most 7, to keep the resource sparsely populated.
    n_optional_keys = np.random.choice(range(save_keys, len(potential_keys_to_drop)))

    # Select which optional keys to keep
    optional_keys_to_keep = np.random.choice(potential_keys_to_drop, size=n_optional_keys, replace=False)
    all_keys = list(resource.keys())
    for key in all_keys:
        if key not in required_keys and key not in optional_keys_to_keep:
            if key == 'status':
                resource[key] = 'unknown'
                continue
            if resourcetype == 'Immunization' and key == "occurrenceDateTime":
                resource['occurrenceString'] = resource[key][:10]
            resource[key] = None


def clean_location(location):
    #location = location.copy()
    del location['meta']
    del location['managingOrganization']
    del location['identifier']
    return location


def remove_digits_humanname(humanname):
    """
    Remove digits from HumanName
    """
    humanname = humanname.copy()
    humanname['family'] = ''.join([char for char in humanname['family'] if not char.isdigit()])
    givennames = []
    for givenname in humanname['given']:
        givennames.append("".join([char for char in givenname if not char.isdigit()]))
    humanname['given'] = givennames
    return humanname

def drop_keys_humanname(humanname):
    """
    Drop keys from HumanName
    """
    humanname = humanname.copy()
    drop_keys = np.random.choice(['family', 'given', 'none'],p=[0.1, 0.1, 0.8])
    if drop_keys == 'family':
        humanname['family'] = None
    elif drop_keys == 'given':
        humanname['given'] = None
    return humanname

def drop_keys_address(address):
    """
    Drop keys from Address
    """
    address = address.copy()
    drop_keys = np.random.choice(['line', 'city', 'state', 'postalCode', 'country', 'none'],p=[0.05, 0.05, 0.05, 0.05, 0.05, 0.75])
    if drop_keys == 'line':
        address['line'] = None
    elif drop_keys == 'city':
        address['city'] = None
    elif drop_keys == 'state':
        address['state'] = None
    elif drop_keys == 'postalCode':
        address['postalCode'] = None
    elif drop_keys == 'country':
        address['country'] = None
    return address


def clean_patient(pat):

    clean_names = []
    for name in pat['name']:
        clean_names.append(drop_keys_humanname(remove_digits_humanname(name)))
    pat['name'] = clean_names

    clean_addresses = []
    for address in pat['address']:
        clean_addresses.append(drop_keys_address(address))
    pat['address'] = clean_addresses

    del pat['text']
    del pat['extension']
    del pat['identifier']
    del pat['address'][0]['extension']

    drop_keys(pat)

    return pat


def find_encounter(pat_id):

    pat_id_reference_key = "Patient/" + pat_id

    # Selecting between 0 and 2 encounters to model 1:1 cardinality, 1:0 and 1:n
    num_encounters = np.random.choice([0, 1, 2], p=[0.3, 0.5, 0.2])
    if num_encounters == 0:
        return []
    encounters_patient = [x.copy() for x in all_encounters if x['subject']
                          ['reference'] == pat_id_reference_key]
    return list(np.random.choice(encounters_patient, size=min(num_encounters, len(encounters_patient)), replace=False))


def find_practitioners(encounter):

    matched_pracs = []

    prac_identifiers = []
    participants = encounter['participant']
    for participant in participants:
        prac_id = participant['individual']['reference'].split("|")[1]
        for practitioner in all_practitioners:
            if 'identifier' not in practitioner.keys():
                continue
            for identifier in practitioner['identifier']:
                if identifier['value'] == prac_id:
                    matched_pracs.append(practitioner.copy())
    return matched_pracs


def find_organisations(encounter):

    matched_orgs = []

    org_identifiers = []
    serviceprovider = encounter['serviceProvider']
    serviceprovider_id = serviceprovider['reference'].split("|")[1]

    for org in all_organizations:
        if 'identifier' not in org.keys():
            continue
        for identifier in org['identifier']:
            if identifier['value'] == serviceprovider_id:
                matched_orgs.append(org.copy())
    return matched_orgs


def find_by_encounter_reference(encounter, candidate_resources):

    num_resources = np.random.choice([0, 1, 2])
    retrieved_resources = []
    if num_resources == 0:
        return retrieved_resources

    for resource in candidate_resources:
        if resource["encounter"]["reference"].split("/")[1] == encounter["id"]:
            retrieved_resources.append(resource.copy())

    return list(np.random.choice(retrieved_resources, size=min(num_resources, len(retrieved_resources)), replace=False))


def find_by_subject_reference(subject, candidate_resources):

    num_resources = np.random.choice([0, 1, 2])
    retrieved_resources = []
    if num_resources == 0:
        return retrieved_resources

    for resource in candidate_resources:
        if resource["subject"]["reference"].split("/")[1] == subject["id"]:
            resource_out = resource.copy()
            del resource_out['encounter']
            retrieved_resources.append(resource_out)

    return list(np.random.choice(retrieved_resources, size=min(num_resources, len(retrieved_resources)), replace=False))


def find_by_patient_reference(patient, candidate_resources):

    num_resources = np.random.choice([0, 1, 2])
    retrieved_resources = []
    if num_resources == 0:
        return retrieved_resources

    for resource in candidate_resources:
        if resource["patient"]["reference"].split("/")[1] == patient["id"]:
            resource_out = resource.copy()
            if "encounter" in resource_out.keys():
                del resource_out['encounter']
            retrieved_resources.append(resource_out)

    return list(np.random.choice(retrieved_resources, size=min(num_resources, len(retrieved_resources)), replace=False))


def clean_organisation(org):
    #org = org.copy()
    if "extension" in org.keys():
        del org['extension']
    del org['identifier']
    drop_keys(org)
    return org


def clean_practitioner(prac):
    #prac = prac.copy()

    clean_names = []
    for name in prac['name']:
        clean_names.append(drop_keys_humanname(remove_digits_humanname(name)))
    prac['name'] = clean_names

    clean_addresses = []
    for address in prac['address']:
        clean_addresses.append(drop_keys_address(address))
    prac['address'] = clean_addresses

    del prac['extension']
    del prac['identifier']
    drop_keys(prac)
    return prac


def clean_encounter(enc, pat_map={}, prac_map={}, org_map={}):
    #enc = enc.copy()
    if "extension" in enc.keys():
        del enc['extension']
    enc['subject']['reference'] = pat_map[enc['subject']
                                          ['reference'].split("/")[1]]
    enc['subject']['display'] = "".join(char for char in enc['subject']['display'] if not char.isdigit())
    for participant in enc['participant']:
        try:
            participant['individual']['reference'] = prac_map[participant['individual']['reference'].split("|")[
            1]]
        except:
            Warning("Practitioner not found")
        enc['serviceProvider']['reference'] = org_map[enc['serviceProvider']
                                                      ['reference'].split("|")[1]]
        participant['individual']['display'] = "".join(char for char in participant['individual']['display'] if not char.isdigit())

    drop_keys(enc)
    return enc


def clean_procedure(procedure, pat_map={}, enc_map={}):
    #procedure = procedure.copy()
    procedure['subject']['reference'] = pat_map[procedure['subject']
                                                ['reference'].split("/")[1]]
    if "display" in procedure['subject'].keys():
        procedure['subject']['display'] = "".join(char for char in procedure['subject']['display'] if not char.isdigit())
    
    if "encounter" in procedure.keys():
        procedure['encounter']['reference'] = enc_map[procedure['encounter']
                                                      ['reference'].split("/")[1]]
    drop_keys(procedure)
    return procedure


def clean_condition(condition, pat_map={}, enc_map={}):
    #condition = condition.copy()
    condition["subject"]["reference"] = pat_map[condition["subject"]
                                                ["reference"].split("/")[1]]
    if "display" in condition['subject'].keys():
        condition['subject']['display'] = "".join(char for char in condition['subject']['display'] if not char.isdigit())
    if "encounter" in condition.keys():
        condition["encounter"]["reference"] = enc_map[condition["encounter"]
                                                      ["reference"].split("/")[1]]
    drop_keys(condition)
    return condition


def clean_allergyintolerance(allergyintolerance, pat_map={}):
    #allergyintolerance = allergyintolerance.copy()
    allergyintolerance["patient"]["reference"] = pat_map[allergyintolerance["patient"]
                                                         ["reference"].split("/")[1]]
    if "display" in allergyintolerance['patient'].keys():
        allergyintolerance['patient']['display'] = "".join(char for char in allergyintolerance['patient']['display'] if not char.isdigit())
    drop_keys(allergyintolerance)
    return allergyintolerance


def clean_immunization(immunization, pat_map={}, enc_map={}):
    #immunization = immunization.copy()
    immunization["patient"]["reference"] = pat_map[immunization["patient"]
                                                   ["reference"].split("/")[1]]
    if "display" in immunization['patient'].keys():
        immunization['patient']['display'] = "".join(char for char in immunization['patient']['display'] if not char.isdigit())

    if "encounter" in immunization.keys():
        immunization["encounter"]["reference"] = enc_map[immunization["encounter"]
                                                         ["reference"].split("/")[1]]
    drop_keys(immunization)
    return immunization


def clean_observation(observation, pat_map={}, enc_map={}):
    #observation = observation.copy()
    observation["subject"]["reference"] = pat_map[observation["subject"]
                                                  ["reference"].split("/")[1]]
    if "display" in observation['subject'].keys():
        observation['subject']['display'] = "".join(char for char in observation['subject']['display'] if not char.isdigit())
    if "encounter" in observation.keys():
        observation["encounter"]["reference"] = enc_map[observation["encounter"]
                                                        ["reference"].split("/")[1]]

    drop_keys(observation)
    return observation


def apply_symbolic_id(resource, mapping):
    if "extension" in resource.keys():
        del resource['extension']
    if "identifier" in resource.keys():
        del resource["identifier"]
    resource['id'] = mapping[resource['id']].split("/")[1]
    return resource


def dedup_list(resources):
    done = []
    resources_out = []
    for item in resources:
        if item['id'] not in done:
            done.append(item['id'])
            resources_out.append(item.copy())
    return resources_out


def build_symbolic_mapping(resources):
    if len(resources) == 0:
        return {}
    resourcetype = resources[0]["resourceType"]
    unique_resource_ids = list(set([r["id"] for r in resources]))

    id_symbolic_map = {
        rid: resourcetype + "/" + str(i+1) for i, rid in enumerate(unique_resource_ids)
    }
    identifier_to_id = {}
    identifier_symbolic_map = {}
    for r in resources:
        if "identifier" in r.keys():
            key = r["identifier"][0]["value"]
            identifier_to_id[key] = r["id"]
            identifier_symbolic_map[key] = id_symbolic_map[r["id"]]
    symbolic_map = {}
    symbolic_map.update(id_symbolic_map)
    symbolic_map.update(identifier_symbolic_map)
    return symbolic_map


# In[56]:
bundle = {
    "resourceType": "Bundle",
    "id": "1",
    "type": "collection",
    "entry": [],
}


all_bundles = []


def find_by_random(enc, pat, candidates):
    target = np.random.choice([enc, pat])
    assert target == enc or target == pat
    resource_out = []
    if target == enc:
        resource_out = find_by_encounter_reference(enc, candidates)
    if target == pat or len(resource_out) == 0:
        resource_out = find_by_subject_reference(pat, candidates)
    return resource_out


for patnr, pat in enumerate(all_patients):
    print(patnr)

    pat_id = pat['id']
    pat_encounter = find_encounter(pat_id)
    pat_encounter_practitioners = []
    pat_encounter_organisations = []
    pat_procedures = []
    pat_conditions = []
    pat_allergies = []
    pat_immunizations = []
    pat_observations = []

    if len(pat_encounter) == 0:
        pat_procedures += find_by_subject_reference(pat, all_procedure)
        pat_conditions += find_by_subject_reference(pat, all_condition)
        pat_allergies += find_by_patient_reference(pat, all_allergyintolerance)
        pat_observations += find_by_subject_reference(pat, all_observation)

    else:
        for enc_idx, enc in enumerate(pat_encounter):
            enc_id = enc['id']
            pat_encounter_practitioners += find_practitioners(enc)
            pat_encounter_organisations += find_organisations(enc)
            pat_procedures += find_by_random(enc, pat, all_procedure)
            pat_conditions += find_by_random(enc, pat, all_condition)
            pat_allergies += find_by_patient_reference(
                pat, all_allergyintolerance)
            pat_immunizations += find_by_encounter_reference(
                enc, all_immunization)
            pat_observations += find_by_random(enc, pat, all_observation)

    # MAKE UNIQUE
    pat_encounter = dedup_list(pat_encounter)
    pat_encounter_practitioners = dedup_list(pat_encounter_practitioners)
    pat_encounter_organisations = dedup_list(pat_encounter_organisations)
    pat_procedures = dedup_list(pat_procedures)
    pat_conditions = dedup_list(pat_conditions)
    pat_allergies = dedup_list(pat_allergies)
    pat_immunizations = dedup_list(pat_immunizations)
    pat_observations = dedup_list(pat_observations)

    # CALCULATE MAPPING FOR RELATIVE IDS
    pat_map = build_symbolic_mapping([pat])
    pat_encounter_map = build_symbolic_mapping(pat_encounter)
    pat_encounter_practitioners_map = build_symbolic_mapping(
        pat_encounter_practitioners)
    pat_encounter_organisations_map = build_symbolic_mapping(
        pat_encounter_organisations)
    pat_procedures_map = build_symbolic_mapping(pat_procedures)
    pat_conditions_map = build_symbolic_mapping(pat_conditions)
    pat_allergies_map = build_symbolic_mapping(pat_allergies)
    pat_immunizations_map = build_symbolic_mapping(pat_immunizations)
    pat_observations_map = build_symbolic_mapping(pat_observations)

    # CLEAN REDUNDANT ELEMENTS, APPLY RELATIVE IDS
    patient = clean_patient(pat)
    for encounter in pat_encounter:
        encounter = clean_encounter(encounter, pat_map=pat_map, prac_map=pat_encounter_practitioners_map,
                                    org_map=pat_encounter_organisations_map)
    for practitioner in pat_encounter_practitioners:
        practitioner = clean_practitioner(practitioner)
    for organisation in pat_encounter_organisations:
        organisation = clean_organisation(organisation)
    for procedure in pat_procedures:
        procedure = clean_procedure(
            procedure, pat_map=pat_map, enc_map=pat_encounter_map)
    for condition in pat_conditions:
        condition = clean_condition(
            condition, pat_map=pat_map, enc_map=pat_encounter_map)
    for allergy in pat_allergies:
        allergy = clean_allergyintolerance(allergy, pat_map=pat_map)
    for immunization in pat_immunizations:
        immunization = clean_immunization(
            immunization, pat_map=pat_map, enc_map=pat_encounter_map)
    for observation in pat_observations:
        observation = clean_observation(
            observation, pat_map=pat_map, enc_map=pat_encounter_map)

    for resources, resource_map in [
        ([patient], pat_map),
        (pat_encounter, pat_encounter_map),
        (pat_encounter_practitioners, pat_encounter_practitioners_map),
        (pat_encounter_organisations, pat_encounter_organisations_map),
        (pat_procedures, pat_procedures_map),
        (pat_conditions, pat_conditions_map),
        (pat_allergies, pat_allergies_map),
        (pat_immunizations, pat_immunizations_map),
        (pat_observations, pat_observations_map)
    ]:
        for resource in resources:
            resource = apply_symbolic_id(resource, resource_map)

    this_bundle = bundle.copy()

    include_patient = np.random.choice([True, False], p=[0.8, 0.2])
    include_encounters = np.random.choice([True, False], p=[0.8, 0.2])
    this_entry_base = pat_allergies + pat_immunizations
    if include_patient:
        this_entry_base = this_entry_base + [patient]
    if include_encounters:
        this_entry_base = this_entry_base + pat_encounter

    this_entry_add = [pat_encounter_practitioners, pat_encounter_organisations,
                      pat_procedures, pat_conditions, pat_observations]
    this_entry_add = [x for x in this_entry_add if len(x) > 0]
    num_additions = np.random.choice([0, 1, 2])
    if num_additions == 0:
        additions_flat = []
    else:
        additions_idx = np.random.choice(
            range(len(this_entry_add)), size=min(num_additions, len(this_entry_add)), replace=False)
        additions = [this_entry_add[i] for i in additions_idx]
        additions_flat = [
            resource for resources_of_type in additions for resource in resources_of_type]
        
    entry_items = this_entry_base + additions_flat
    this_bundle["entry"] = [{"resource": resource} for resource in entry_items]

    bundle_validation = Bundle.parse_raw(json.dumps(this_bundle))

    all_bundles.append(this_bundle)



def build_notes(batch_num, batch_size=10):
    print("building notes", batch_num)
    dataset = {}
    dataset["fhir"] = []
    dataset["note"] = []
    bundles = all_bundles[batch_num*batch_size:(batch_num+1)*batch_size]
    for i, bundle in enumerate(bundles):
        pat_copy = bundle.copy()
        note = convert_to_note(pat_copy)
        if note:
            dataset["fhir"].append(json.dumps(bundle))
            dataset["note"].append(note)

        time.sleep(1)
        print(i)

        
    pd.DataFrame(dataset).to_csv(f"train_{batch_num}.csv", index=False)



for i in range(100):
        build_notes(i)
        time.sleep(60)



"""
dataset = {}
dataset["fhir"] = []
dataset["note"] = []
for i, pat in enumerate(all_bundles[2200:2220]):
    note = convert_to_note(pat)
    if note:
        dataset["fhir"].append(json.dumps(pat))
        dataset["note"].append(note)
    print(i)

pd.DataFrame(dataset).to_csv("validation.csv", index=False)


# In[27]:


dataset = {}
dataset["fhir"] = []
dataset["note"] = []
for i, pat in enumerate(all_bundles[2220:2300]):
    note = convert_to_note(pat)
    if note:
        dataset["fhir"].append(json.dumps(pat))
        dataset["note"].append(note)
    time.sleep(1)
    print(round(i))

pd.DataFrame(dataset).to_csv("test.csv", index=False)


# In[ ]:


# In[ ]:

"""