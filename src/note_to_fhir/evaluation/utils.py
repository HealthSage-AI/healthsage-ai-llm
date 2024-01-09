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
from src.note_to_fhir.evaluation.datamodels import FhirScore, ElementDetails, FhirDiff
from src.note_to_fhir.evaluation.fhirmodels import *

from typing import List
import warnings
import plotly.graph_objects as go
from collections import defaultdict

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

        element_details = ElementDetails(key=name,
                                        fhirtype=fhirtype,
                                        required=required,
                                        is_leaf=fhirtype_is_leaf(fhirtype),
                                        is_struct=fhirtype_is_struct(fhirtype),
                                        is_array=fhirtype_is_array(fhirtype),
                                        array_item_type=array_item_type
                                        )

            
        resource_details.append(element_details)
            
    return resource_details

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
    warnings.warn(f"NotImplemented; arrays are assumed to be in identical order.")
    return match_list_len(arr1, arr2)

def convert_to_defaultdict(obj) -> defaultdict:
    if type(obj) == dict or obj == None:
        return defaultdict(dict, obj) if obj else defaultdict(dict)
    else:
        return obj
    
def get_resource_type(resource, resource_name) -> str:
    """Determine the resource type of a resource

    Args:
        resource (Any): The FHIR resource, can be any datatype.

    Returns:
        str: string representation of the resource type
    """
    if isinstance(resource, dict):
        if resource['resourceType']:
            return resource['resourceType']
    return resource_name


def calculate_diff(diff: FhirDiff) -> FhirDiff:
    """Process FhirDiff to calculate FhirDiff.fhirscore

    Args:
        diff (FhirDiff): comparison object containing the fhir to be compared

    Returns:
        FhirComparison: comparison with fhirscore attribute calculated.
    """
    resource_type = get_resource_type(diff.fhir_true, diff.resource_name)

    if fhirtype_is_leaf(resource_type):
        diff.score = compare_leaf(diff.fhir_true, diff.fhir_pred)
        return diff

    Resource = eval(resource_type)

    resource_details = get_resource_details(Resource)
    for element_details in resource_details:

        # Skip if the element is absent in both fhir_true and fhir_pred.
        if element_details.key not in diff.fhir_pred.keys() and element_details.key not in diff.fhir_true.keys():
            continue
        if diff.fhir_true[element_details.key] is None and diff.fhir_pred[element_details.key] is None:
            continue

        # If the element is a struct (dictionary) with arbitrary depth, handle recursively
        fhir_true_child, fhir_pred_child = convert_to_defaultdict(diff.fhir_true[element_details.key]), convert_to_defaultdict(diff.fhir_pred[element_details.key])
        if element_details.is_struct:
            childdiff = FhirDiff(fhir_true=fhir_true_child,
                                 fhir_pred=fhir_pred_child,
                                 resource_name=element_details.fhirtype,
                                 parent=diff,
                                 key=element_details.key
                                 )
            childdiff = calculate_diff(childdiff)
            childscore = childdiff.score
            diff.children[element_details.key] = childdiff

        # If the element is an array, handle recursively on each array item
        elif element_details.is_array:
            diff.children[element_details.key] = []
            fhir_true_child, fhir_pred_child = match_list_len(diff.fhir_true[element_details.key], diff.fhir_pred[element_details.key])

            i=1
            childscore = FhirScore()
            for fhir_true_child_item, fhir_pred_child_item in zip(fhir_true_child, fhir_pred_child):
                fhir_pred_child_item = convert_to_defaultdict(fhir_pred_child_item)
                fhir_true_child_item = convert_to_defaultdict(fhir_true_child_item)
                childdiff_item = FhirDiff(fhir_true=fhir_true_child_item,
                                          fhir_pred=fhir_pred_child_item,
                                          resource_name=element_details.array_item_type,
                                          parent=diff,
                                          entry_nr=str(i),
                                          key=element_details.key)
                childdiff_item = calculate_diff(childdiff_item)
                diff.children[element_details.key].append(childdiff_item)
                childscore = childscore + childdiff_item.score
                i+=1

        # If the element is a leaf, calculate the score directly
        elif element_details.is_leaf:
            childdiff = FhirDiff(fhir_true = diff.fhir_true[element_details.key],
                                 fhir_pred = diff.fhir_pred[element_details.key],
                                 resource_name=element_details.fhirtype,
                                 parent=diff,
                                 key=element_details.key
                                 )
            childscore = compare_leaf(diff.fhir_true[element_details.key],
                                 diff.fhir_pred[element_details.key]
                                 )
            childdiff.score = childscore
            diff.children[element_details.key] = childdiff

        # Add the child node score to the current score
        diff.score = diff.score + childscore
    
    return diff

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
        fhirscore = FhirScore(n_deletions=1, n_leaves=1)  # miss
    elif not element_true:
        fhirscore = FhirScore(n_additions=1, n_leaves=1)  # hallucination
    elif element_true != element_pred:
        fhirscore = FhirScore(n_modifications=1, n_leaves=1)  # mistake
    elif element_true == element_pred:
        fhirscore = FhirScore(n_matches=1, n_leaves=1)  # correct
    return fhirscore