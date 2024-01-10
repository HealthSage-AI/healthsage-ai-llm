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

from pydantic import BaseModel, computed_field
from typing import Any, Optional

class FhirScore(BaseModel):

    n_leaves: int = 0  # The number of leaf nodes in this object
    n_additions: int = 0  # The number of hallucinated leaf nodes, a.k.a. "False Positives"
    n_deletions: int = 0  #  The number of missing leaf nodes, a.k.a. "False Negatives"
    n_modifications: int = 0  # The number of changes leaf nodes a.k.a. "Mistakes"
    n_matches: int = 0  # The number of identical leaf nodes, a.k.a. "True Positives"
    n_valid: int = 0
    
    @computed_field
    @property
    def accuracy(self) -> float:  # The overall accuracy
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
                         n_matches=self.n_matches+other.n_matches,
                         n_valid=self.n_valid + other.n_valid)
    
    
class ElementDetails(BaseModel):
    
    key: str
    fhirtype: str
    required: bool
    is_leaf: bool
    is_array: bool
    is_struct: bool
    array_item_type: Optional[str]

    
class FhirDiff(BaseModel):

    fhir_true: Any
    fhir_pred: Any
    resource_name: str # resource type or fhir type 
    parent: 'FhirDiff' = None
    children: dict = {}
    entry_nr: str = ""  # For lists, tracking index
    key: str = ""  # What the element is named in its parent object
    score: FhirScore = FhirScore()

    @computed_field
    @property
    def label(self) -> str:
        """Labels are used to identify the node in the FHIR tree

        Returns:
            str: node label describing PARENT.KEY.ENTRY_NR where parent, key and entry_nr are optional
        """
        parent_label = "" if not self.parent else self.parent.label
        keylabel = self.key if self.key != "resource" else self.resource_type
        label = ".".join([parent_label, keylabel, self.entry_nr]).strip(".")
        return label
    
    @computed_field
    @property
    def resource_type(self) -> str:
        if isinstance(self.fhir_true, dict):
            if self.fhir_true["resourceType"]:
                return self.fhir_true["resourceType"]
        return self.resource_name