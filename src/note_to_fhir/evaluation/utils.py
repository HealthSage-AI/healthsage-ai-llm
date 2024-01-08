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
from fhir.resources.R4B.patient import Patient
from fhir.resources.R4B.encounter import Encounter
from fhir.resources.R4B.organization import Organization
from fhir.resources.R4B.practitioner import Practitioner
from fhir.resources.R4B.procedure import Procedure
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.allergyintolerance import AllergyIntolerance
from fhir.resources.R4B.immunization import Immunization
from fhir.resources.R4B.observation import Observation
from evaluation.dataclasses import FhirScore, ElementDetails, FhirDiff
from typing import List
import warnings

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

def get_resource_details(Resource) -> List[ElementDetails]:
    """Get the details of a certain fhir resource that are relevant to evaluation in a friendly format.

    Args:
        Resource (fhir.resources): Resource Metadata

    Returns:
        ResourceDetails: details about a fhir resource
    """

    resource_details = []

    for name, spec in Resource.schema()['properties'].items():
        if 'element_property' not in spec.keys():
            continue
        if not spec['element_property']:
            continue
        if 'type' not in spec.keys():
            continue        

        required = False if 'element_required' not in spec.keys() else spec['element_required']

        fhirtype = spec['type']
        array_item_type = None
        if fhirtype == 'array':
            array_item_type = spec['items']['type']

        element_details = ElementDetails(name=name,
                                        fhirtype=fhirtype,
                                        required=required,
                                        is_leaf=fhirtype_is_leaf(fhirtype),
                                        is_struct=fhirtype_is_struct(fhirtype),
                                        is_array=fhirtype_is_array(fhirtype),
                                        array_item_type=array_item_type
                                        )

            
        element_details.append(resource_details)
            
    return element_details

def match_list_len(list_1: list, list_2: list) -> tuple:
    """Iteratively appends None to shortest list untill it matches longest list
    Args:
        list_1 (list): A list of items
        list_2 (list): A list of items

    Returns:
        tuple: The respectives lists but of equal length, imputed with None.
    """
    list_1 = list_1 if list_1 else []
    list_2 = list_2 if list_2 else []
    len_1 = len(list_1)
    len_2 = len(list_2)
    max_len = max(len_1, len_2)
    for i in range(max_len):
        if i >= len_1:
            list_1.append(None)
        elif i >= len_2:
            list_2.append(None)
        else:
            continue
    return list_1, list_2

def validate_resource(resource: dict) -> bool:
    """Checks whether a FHIR resource is valid

    Args:
        resource (dict): A dictionary representing a FHIR R4B resource.

    Returns:
        bool: True if the resource was succesfully parsed, False otherwise.
    """
    assert "resourceType" in resource.keys(), "resourceType unspecified"
    try:
        ResourceClass = resource_mapping[resource['resourceType']]
        resource = ResourceClass.parse_raw(json.dumps(resource))
        return True
    except:
        return False
    
def fhirtype_is_struct(fhirtype: str) -> bool:
    """Check whether fhirtype is a struct by checking if the first letter of the type is a capital letter.

    Args:
        fhirtype (str): fhirtype as specified by fhir.resources

    Returns:
        bool: True if fhirtype is struct, False otherwise
    """
    return fhirtype[0] != fhirtype[0].lower()

def fhirtype_is_array(fhirtype: str) -> bool:
    """Check whether fhirtype is array

    Args:
        fhirtype (str): fhirtype as specified by fhir.resources

    Returns:
        bool: True if fhirtype is array, False otherwise
    """
    return fhirtype == 'array'

def fhirtype_is_leaf(fhirtype) -> bool:
    """Check whether a fhirtype is a leaf. i.e. whether the fhirtype contains no nested fields.

    Args:
        fhirtype (str): fhirtype as specified by fhir.resources

    Returns:
        bool: True if fhirtype is leaf, False otherwise
    """
    return fhirtype in ["boolean", "integer", "string", "decimal"]

def map_align_arrays(arr1, arr2):
    """Maps two arrays to eachother and aligns them in corresponding order.

    Args:
        arr1 (list): list of fhir elements
        arr2 (list): list of fhir elements

    Returns:
        arr1, arr2: Where arr1[i] corresponds to arr2[i]
    """
    warnings.warn(f"Notimplemented; arrays are assumed to be in identical order.")
    return match_list_len(arr1, arr2)

def calculate_diff(diff: FhirDiff) -> FhirDiff:
    """Process FhirDiff to calculate FhirDiff.fhirscore

    Args:
        diff (FhirDiff): comparison object containing the fhir to be compared

    Returns:
        FhirComparison: comparison with fhirscore attribute calculated.
    """
    resource_name = diff.resource_name
    Resource = eval(resource_name)
    resource_details = get_resource_details(Resource)
    for element_details in resource_details:

        # Skip if the element is absent in both fhir_true and fhir_pred.
        if element_details.key not in diff.fhir_pred.keys() and element_details.key not in diff.fhir_true.keys():
            continue
        if diff.fhir_true[element_details.key] is None and diff.fhir_pred[element_details.key] is None:
            continue

        # If the element is a struct (dictionary) with arbitrary depth, handle recursively
        if element_details.is_struct:
            childdiff = FhirDiff(diff.fhir_true[element_details.key],
                                 diff.fhir_pred[element_details.key],
                                 element_details.fhirtype,
                                 parent=diff,
                                 key=element_details.key
                                 )
            childdiff = calculate_diff(childdiff)
            childscore = childdiff.score
            diff.children[element_details.key] = childdiff

        # If the element is an array, handle recursively on each array item
        elif element_details.is_array:
            fhir_true_child, fhir_pred_child = match_list_len(diff.fhir_true[element_details.key], diff.fhir_pred[element_details.key])
            i=1
            childscore = FhirScore()
            for fhir_true_child_item, fhir_pred_child_item in zip(fhir_true_child, fhir_pred_child):
                i+=1
                childdiff_item = FhirDiff(fhir_true_child_item,
                                          fhir_pred_child_item,
                                          resource_name=element_details.array_item_type,
                                          parent=diff,
                                          entry_nr=str(i),
                                          key=element_details.key)
                childdiff_item = calculate_diff(childdiff_item)
                childscore = childscore + childdiff_item.score

        # If the element is a leaf (terminal) node, calculate the final score



        diff.score = diff.score + childscore









def process_comparison_leaf(comparison: FhirDiff) -> FhirDiff:
    """Process leaf node of a comparison

    Args:
        comparison (FhirComparison): _description_

    Returns:
        FhirComparison: comparison with fhirscore attribute calculated.
    """

def compare_leaf(element_true: any, element_pred: any) -> FhirScore:
    """Compares two leaf nodes of a FHIR structure

    Args:
        element_true (any): The ground truth fhir element
        element_pred (any): The predicted fhir element

    Returns:
        FhirScore: object containing score for the leaf node.
    """
    assert not (element_pred is None and element_true is None), "Element can't both be None for comparison"
    if not element_pred:
        fhirscore = FhirScore(n_deletions=1, n_leaves=1)  # a.k.a. missing prediction
    elif not element_true:
        fhirscore = FhirScore(n_additions=1, n_leaves=1)  # a.k.a. hallucination
    elif element_true != element_pred:
        fhirscore = FhirScore(n_modifications=1, n_leaves=1)  # a.k.a. mistake
    elif element_true == element_pred:
        fhirscore = FhirScore(n_matches=1, n_leaves=1)  # a.k.a. correct
    return fhirscore

def preprocess_for_treemap(comparison: FhirDiff):
    """Flattens a nested comparison object for plotly treemaps

    Args:
        comparison (FhirComparison): FhirComparison object

    Returns:
        (labels, parents, values):
            - labels define the "name" of the node
            - parents define the parent label
            - values or the content of the treemap 
    """

    # Current Node
    labels = [comparison.label]
    parents = [comparison.parent.label] if comparison.parent else [""]
    values = [comparison]

    if not comparison.children:
        return labels, parents, values
    
    for child_comparison in comparison.children.values():
        if type(child_comparison) == list:
            for child_comparison_item in child_comparison:
                new_labels, new_parents, new_values = preprocess_for_treemap(child_comparison_item)
                labels = labels + new_labels
                parents = parents + new_parents
                values = values + new_values

        else:
            new_labels, new_parents, new_values = preprocess_for_treemap(child_comparison)
            labels = labels + new_labels
            parents = parents + new_parents
            values = values + new_values

    return labels, parents, values