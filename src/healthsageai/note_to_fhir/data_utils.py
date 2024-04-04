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

def drop_code(coding: dict) -> dict:
    """Drop code for SNOMED and Loinc codings

    Args:
        coding (dict): coding

    Returns:
        dict: Copy of coding with SNOMED and Loinc codes deleted
    """
    coding_out = coding.copy()
    if "code" in coding.keys():
        del coding_out['code']
    return coding_out

def drop_snomed_loinc(d):
    """Recursively drop Nones in dict d and return a new dict"""
    dd = {}
    for k, v in d.items():
        if isinstance(v, dict):
            dd[k] = drop_snomed_loinc(v)
        elif isinstance(v, list) and k != "coding":
            # note: Nones in lists are not dropped
            dd[k] = [drop_snomed_loinc(vv) if isinstance(vv, dict) else vv
                            for vv in v]
        elif k == 'coding' and isinstance(v, list):
            dd[k] = [drop_code(code) if "snomed" in code.get("system","") or "loinc" in code.get("system","") else code for code in v]
        else:
            dd[k] = v
            
    return dd


def remove_snomed_loinc_code_for_coding(key, val):
    if key == 'code' and isinstance(val['coding'], list):
        val['coding'] = [code for code in val['coding'] if
                         code['system'] not in ['http://snomed.info/sct', 'http://loinc.org']]

    return val


def clean_fhir_resource(fhir: dict) -> dict:
    return {key: remove_snomed_loinc_code_for_coding(key, val) for (key, val) in drop_nones(fhir).items()}


def filter_supported_fhir_resources(resources: list) -> list:
    return [res for res in resources if
            res['resourceType'] in ['Observation', 'Condition', 'Procedure', 'Encounter', 'Patient', 'Organization',
                                    'Location', 'Practitioner', 'Immunization', 'AllergyIntolerance']]


def drop_nones(d: dict) -> dict:
    """Recursively drop Nones in dict d and return a new dict"""
    dd = {}
    for k, v in d.items():
        if isinstance(v, dict):
            dd[k] = drop_nones(v)
        elif isinstance(v, (list, set, tuple)):
            # note: Nones in lists are not dropped
            dd[k] = type(v)(drop_nones(vv) if isinstance(vv, dict) else vv
                            for vv in v)
        elif v is not None:
            dd[k] = v
    return dd
