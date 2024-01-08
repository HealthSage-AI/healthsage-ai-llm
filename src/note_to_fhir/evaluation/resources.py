#  Copyright (c) 2024. HealthSage AI.
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
from evaluation.dataclasses import Patient, Encounter, Organization, Practitioner, Procedure, Condition, AllergyIntolerance, Immunization, Observation
from pydantic import BaseModel, computed_field

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

def validate_resource(resource: dict) -> bool:
    assert "resourceType" in resource.keys(), "resourceType unspecified"
    try:
        ResourceClass = resource_mapping[resource['resourceType']]
        resource = ResourceClass.parse_raw(json.dumps(resource))
        return True
    except:
        return False
    
def fhirtype_is_struct(fhirtype: str) -> bool:
    return fhirtype[0] != fhirtype[0].lower()

def fhirtype_is_array(fhirtype) -> bool:
    return fhirtype == 'array'

def fhirtype_is_leaf(fhirtype) -> bool:
    return fhirtype in ["boolean", "integer", "string", "decimal"]

class FhirScore(BaseModel):

    n_leaves: int = 0  # The number of leaf nodes in this object
    n_additions: int = 0  # The number of hallucinated leaf nodes, a.k.a. "False Positives"
    n_deletions: int = 0  #  The number of missing leaf nodes, a.k.a. "False Negatives"
    n_modifications: int = 0  # The number of changes leaf nodes a.k.a. "Mistakes"
    n_matches: int = 0  # The number of identical leaf nodes, a.k.a. "True Positives"
    
    @computed_field
    @property
    def score(self) -> float:  # The overall accuracy
        return self.n_matches / max(self.n_leaves, 1)
    
    @computed_field
    @property
    def precision(self) -> float: # What % of generated FHIR was correct
        return self.n_matches / max(self.n_matches + self.n_additions + self.n_modifications, 1)
    
    @computed_field
    @property
    def recall(self) -> float:  # What % of reference FHIR was correctly generated
        return self.n_matches / max(self.n_matches + self.n_deletions + self.n_deletions, 1)
    
    def __add__(self, other: 'FhirScore'):
        return FhirScore(n_leaves=self.n_leaves + other.n_leaves,
                         n_additions=self.n_additions + other.n_additions,
                         n_deletions=self.n_deletions + other.n_deletions,
                         n_modifications=self.n_modifications + other.n_modifications,
                         n_matches=self.n_matches+other.n_matches)