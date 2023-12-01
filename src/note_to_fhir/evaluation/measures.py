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

import json
import pandas as pd
import warnings
from fhirmodels import assessmentmodel_mapping
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.practitioner import Practitioner
from fhir.resources.R4B.procedure import Procedure
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.allergyintolerance import AllergyIntolerance
from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.observation import Observation

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

def validate_resource(resource, source=''):
    try:
        ResourceClass = resource_mapping[resource['resourceType']]
        resource = ResourceClass.parse_raw(json.dumps(resource))
        return True
    except:
        return False

class ResourceDistance(object):

    def __init__(self, resource_true, resource_pred, assessment_model):
        self.assessment = assessment_model
        self.resource_true = resource_true
        self.resource_pred = resource_pred
        self.missing = list()
        self.added = list()
        self.changed = list()
        self.ignored = list()
        self.correct = list()
        self.missing_in_reference_resource = list()
        self.hallucinated_in_reference_resource = list()
        self.n_elements = 0
        self.get_accuracy()
        self.resource_true_is_valid = validate_resource(resource_true, source="True")
        self.resource_pred_is_valid = validate_resource(resource_pred, source="Pred")

    @property
    def mistakes(self):
        return self.missing + self.added + self.changed

    def get_precision(self):
        n = len(self.resource_pred.keys())
        tp = 0
        for key in self.resource_pred.keys():
            keyname = self.assessment[key]['name']
            required = self.assessment[key]['required']
            ignored = self.assessment[key]['ignore']
            assessment = self.assessment[key]['expected_value_assessment']
            correct = self.eval_element(keyname, required=required, ignored=ignored, assessment=assessment)
            if correct is None:
                n -= 1
                continue
            if correct:
                tp += 1
        return tp/n

    def get_recall(self):
        n = len(self.resource_true.keys())
        tp = 0
        for key in self.resource_true.keys():
            keyname = self.assessment[key]['name']
            required = self.assessment[key]['required']
            ignored = self.assessment[key]['ignore']
            assessment = self.assessment[key]['expected_value_assessment']
            correct = self.eval_element(keyname, required=required, ignored=ignored, assessment=assessment)
            if correct is None:
                n -= 1
                continue
            if correct:
                tp += 1
        return tp/n

    def get_accuracy(self):
        if self.resource_pred == {}:
            return 0.
        all_keys = self.assessment.keys()
        n = len(all_keys)
        tp = 0
        for key in self.assessment.keys():
            keyname = self.assessment[key]['name']
            required = self.assessment[key]['required']
            ignored = self.assessment[key]['ignore']
            assessment = self.assessment[key]['expected_value_assessment']
            correct = self.eval_element(keyname, required=required, ignored=ignored, assessment=assessment)
            if correct is None:
                n -= 1
                continue
            elif correct:
                tp += 1
        self.n_elements = n
        if n == 0:
            return None
        return tp/n

    def eval_element(self, keyname, required=False, ignored=False, assessment="compare_string"):


        if keyname in self.changed:
            return False
        if keyname in self.correct:
            return True
        if keyname in self.ignored:
            return None
        if keyname in self.missing:
            return False
        if keyname in self.added:
            return False
        
        assessment_keynames = [x["name"] for x in self.assessment.values()]
        if keyname not in assessment_keynames:
            if keyname in self.resource_pred.keys() and keyname not in self.resource_true.keys():
                self.added.append(keyname)
                return False
            elif keyname in self.resource_true.keys():
                self.hallucinated_in_reference_resource.append(keyname)
                return False

        # Check if key should be considered for evaluation
        if ignored:
            self.ignored.append(keyname)
            return None
        # Check if key is hallucinated
        if keyname not in self.resource_true.keys() and keyname in self.resource_pred.keys():
            self.added.append(keyname)
            return False
        # Check if key is missing w.r.t. the true resource
        if keyname not in self.resource_pred.keys() and keyname in self.resource_true.keys():
            self.missing.append(keyname)
            return False
        # Check if key is missing w.r.t. the assessment model
        if keyname not in self.resource_pred.keys() and required:
            self.missing_in_reference_resource.append(keyname)
            return False
        
        # Check if element is irrelevant
        if keyname not in self.resource_pred.keys() and keyname not in self.resource_true.keys():
            return None
        
        # Compare intersection


        # Naive string comparison
        if assessment == "compare_string":
            if "system" in str(self.resource_true[keyname]).lower():
                warnings.warn(f"Comparing unsupported Coding System for {str(self.resource_true[keyname])}")
            is_match = str(self.resource_true[keyname]).lower() == str(
                self.resource_pred[keyname]).lower()
            if is_match:
                self.correct.append(keyname)
            else:
                self.changed.append(keyname)
            return is_match
        
        # Always correct
        if assessment == "any":
            self.correct.append(keyname)
            return True
        
        # Compare with fixed value
        if assessment == "fixed":
            is_match = self.assessment[keyname].expected_value == self.resource_pred[keyname]
            if is_match:
                self.correct.append(keyname)
            else:
                self.changed.append(keyname)
            return is_match
        
        if assessment == "compare_coding":
            is_match = self.compare_coding(
                self.resource_true[keyname], self.resource_pred[keyname])
            if is_match:
                self.correct.append(keyname)
            else:
                self.changed.append(keyname)
            return is_match
        
    def compare_coding(self, coding_true, coding_pred, relaxed=True):
        """
        Compare two coding objects
        """
        coding_true, coding_pred = self.process_coding(coding_true), self.process_coding(coding_pred)
        if "system" not in coding_true.keys() or "system" not in coding_pred.keys():
            warnings.warn(f"Missing system key in coding: {coding_true} or {coding_pred}")
        if "system" not in coding_pred.keys():
            return False
        code_match = coding_true["code"] == coding_pred["code"]
        system_match = coding_true["system"] == coding_pred["system"]
        display_match = coding_true["display"] == coding_pred["display"]
        code_key_match = ("code" in coding_true.keys()) == ("code" in coding_pred.keys())
        display_key_match = ("display" in coding_true.keys()) == ("display" in coding_pred.keys())
        if relaxed and system_match and code_key_match and display_key_match:
            return None
        elif relaxed:
            return False
        else:
            return system_match and code_match and display_match
        
    def process_coding(self, coding):
        while type(coding) == list:
            if len(coding) > 1:
                warnings.warn(f"Multiple codings found: {coding}")
            coding = coding[0]
        if "coding" in coding.keys():
            coding = self.process_coding(coding["coding"])
        return coding




class ResourceBundleDistance(object):

    def __init__(self, bundle_true, bundle_pred):
        self.bundle_true = bundle_true
        self.bundle_pred = bundle_pred
        self.missing_resources = list()
        self.redundant_resources = list()
        self.incorrect_resources = list()
        self.correct_resources = list()
        self.resource_mapping = {}  # Resource id True -> Resource id Pred
        self.resource_distances = list()
        self.full_mapping = pd.DataFrame()
        self.init_full_mapping()
        self.map_resources(assessmentmodel_mapping)
        self.bundle_accuracy = self.full_mapping.max(axis=1).mean()
        self.bundle_subscores, self.entry_scores = self.calculate_bundle_score()
        self.bundle_validity = sum([validate_resource(x) for x in self.bundle_pred])/len(self.bundle_pred)


        
    def calculate_bundle_score(self):
        bundle_score = self.full_mapping.max(axis=1).mean()
        score_per_entry = self.full_mapping.max(axis=1)
        df = pd.DataFrame(score_per_entry)
        df = df.reset_index()
        df['resource_type'] = df['index'].apply(lambda x: x.split("/")[0])
        df.columns = ['index', 'accuracy', 'resource_type']
        df = df[['accuracy', 'resource_type']]
        results = df.groupby('resource_type').mean()
        results.loc["Bundle", "accuracy"] = bundle_score
        return results, df
        
    def init_full_mapping(self):
        print(self.bundle_pred)
        for x in self.bundle_pred:
            if 'id' not in x.keys():
                x['id'] = "1"
                warnings.warn(f"Missing id in resource: {x}")
        columns = [x['resourceType'] + "/" + x['id'] for x in self.bundle_pred]
        index = [x['resourceType'] + "/" + x['id'] for x in self.bundle_true]
        self.full_mapping = pd.DataFrame(index=index, columns=columns)

    def map_resources(self, assessmentmodel_mapping):
        bundle_true = self.bundle_true.copy()
        bundle_pred = self.bundle_pred.copy()

        min_match = 0.6

        for resource_true in bundle_true:
            best_match = min_match
            for resource_pred in bundle_pred:
                resource_true_id = resource_true["resourceType"] + "/" + resource_true["id"]
                resource_pred_id = resource_pred["resourceType"] + "/" + resource_pred["id"]

                if resource_true["resourceType"] != resource_pred["resourceType"]:
                    self.full_mapping.loc[resource_true_id, resource_pred_id] = 0.
                    continue

                resource_type = resource_true["resourceType"]
                assessmentmodel = assessmentmodel_mapping[resource_type]
                resource_distance = ResourceDistance(
                    resource_true, resource_pred, assessment_model=assessmentmodel().dict()
                )
                self.full_mapping.loc[resource_true_id, resource_pred_id] = resource_distance.get_accuracy()
        

