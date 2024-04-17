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

from pydantic import BaseModel, computed_field, field_validator, Field
from typing import Any, Optional
from collections import defaultdict


class FhirValiditionScore(BaseModel):
    n_nodes: int = 0
    n_valid_nodes: int = 0
    n_invalid_nodes: int = 0
    self_is_valid: Optional[bool] = None

    @computed_field
    @property
    def validation_score(self) -> float:
        if self.n_nodes == 0:
            return None
        else:
            return self.n_valid_nodes / self.n_nodes


class FhirScore(BaseModel):
    n_leaves: int = 0  # The number of leaf nodes in this object
    n_additions: int = 0  # n hallucinated leaf nodes, a.k.a. "False Positives"
    n_deletions: int = 0  #  n of missing leaf nodes, a.k.a. "False Negatives"
    n_modifications: int = 0  # n of changes leaf nodes a.k.a. "Mistakes"
    n_matches: int = 0  # n of identical leaf nodes, a.k.a. "True Positives"
    is_valid: Optional[bool] = None

    @computed_field
    @property
    def accuracy(self) -> float:  # The overall accuracy
        if self.n_leaves == 0:
            return None
        return self.n_matches / self.n_leaves

    @computed_field
    @property
    def precision(self) -> float:  # What % of generated FHIR was correct
        total = self.n_matches + self.n_additions + self.n_modifications
        if total == 0:
            return None
        return self.n_matches / total

    @computed_field
    @property
    def recall(self) -> float:  # What % of reference FHIR was correctly generated
        total = self.n_matches + self.n_deletions + self.n_modifications
        if total == 0:
            return None
        return self.n_matches / total

    def __add__(self, other: "FhirScore"):
        if not isinstance(other, FhirScore):
            return self
        return FhirScore(
            n_leaves=self.n_leaves + other.n_leaves,
            n_additions=self.n_additions + other.n_additions,
            n_deletions=self.n_deletions + other.n_deletions,
            n_modifications=self.n_modifications + other.n_modifications,
            n_matches=self.n_matches + other.n_matches,
            is_valid=self.is_valid and other.is_valid,
        )

    def __radd__(self, other: Any):
        if not isinstance(other, FhirScore):
            return self
        else:
            return self.__add__(other)


class ElementDetails(BaseModel):
    key: str
    fhirtype: str
    required: bool
    is_leaf: bool
    is_array: bool
    is_struct: bool
    array_item_type: Optional[str]


class FhirDiff(BaseModel):
    fhir_true: Any = Field(repr=False)
    fhir_pred: Any = Field(repr=False)
    resource_name: str  # resource type or fhir type
    parent: Optional["FhirDiff"] = Field(default_factory=lambda: None, repr=False)
    children: dict = Field(default_factory=dict, repr=False)
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
        if isinstance(self.fhir_true, dict) and len(self.fhir_true) > 0:
            if self.fhir_true["resourceType"]:
                return self.fhir_true["resourceType"]
        return self.resource_name

    @field_validator("fhir_true", "fhir_pred", mode="before")
    def convert_to_defaultdict(cls, v):
        if isinstance(v, dict):
            return defaultdict(lambda: {}, v)
        if v is None:
            return defaultdict(lambda: {})
        return v
