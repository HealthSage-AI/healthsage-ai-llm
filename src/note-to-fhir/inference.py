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

import os

import dotenv
import openai
import requests

from data_utils import clean_fhir_resource
from parsers import parse_json_markdown
from templates.complex import count_resource_template
from templates.simple import template, unique_resource_template, resource_to_note_template, merge_notes_template, \
    chunk_input_note_template, summarize_input_template

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENAI_API_ENDPOINT",
                            "https://healthsage-openai-gpt4.openai.azure.com/")
openai.api_type = 'azure'
openai.api_version = '2023-05-15'

deployment_name = "healthsage-gpt4-32k"

OPENAI_MODEL = "gpt-4"


def get_openai_chatcompletion_gpt35(messages, max_tokens=3500, model="gpt-35-turbo", temperature=0):
    response = openai.ChatCompletion.create(engine="gpt-35-16k",
                                            messages=messages,
                                            max_tokens=max_tokens,
                                            temperature=temperature
                                            )

    return response


def get_openai_chatcompletion(messages, max_tokens=3500, model=OPENAI_MODEL, temperature=0):
    response = openai.ChatCompletion.create(engine=deployment_name,
                                            model=model,
                                            messages=messages,
                                            max_tokens=max_tokens,
                                            temperature=temperature
                                            )

    return response


def convert_to_fhir(note: str, model: str):
    """
    Ask openai to convert a clinical note to FHIR R4 format.
    """
    if model == "GPT-4":
        return convert_to_fhir_gpt4(note)
    return convert_to_fhir_llama(note)


def convert_to_fhir_gpt4(note):
    prompt = template.format(note=note)
    messages = [
        {"role": "system", "content": "you are a program that converts unstructured to structured data"},
        {"role": "user", "content": prompt}]

    response = get_openai_chatcompletion(messages)
    return parse_json_markdown(response.to_dict()['choices'][0]['message']['content'])


def convert_to_fhir_llama(note: str):
    return [clean_fhir_resource(entry['resource']) for entry in get_azure_llama_completion({"message": note}).get('entry', [])]


def get_azure_llama_completion(note: dict):
    url = 'https://ept-notetofhir-nonprd-weu-001.westeurope.inference.ml.azure.com/score'
    api_key = os.getenv('AZURE_ML_ENDPOINT_KEY')
    if not api_key:
        raise Exception("AZURE_ML_ENDPOINT_KEY should be set in .env file")

    resp = requests.post(url, json=note,
                         headers={'Content-Type': 'application/json', 'Authorization': ('Bearer ' + api_key),
                                  'azureml-model-deployment': 'red'})
    resp.raise_for_status()
    return resp.json()


def convert_to_fhir_resource(note: str, resource: str):
    """
    Convert a clinical note to a specific FHIR R4 resource of a specific type
    """
    prompt = unique_resource_template.format(note=note, resource=resource)
    messages = [
        {"role": "system", "content": "you are a program that converts unstructured to structured data"},
        {"role": "user", "content": prompt}]
    response = get_openai_chatcompletion(messages)
    return parse_json_markdown(response.to_dict()['choices'][0]['message']['content'])


def chunk_input(note: str):
    """
    Split a clinical note into subnotes - warning - doesn't work very well
    """
    prompt = chunk_input_note_template.format(note=note)
    messages = [
        {"role": "system", "content": "you are a program that splits data for parallel processing"},
        {"role": "user", "content": prompt}]
    response = get_openai_chatcompletion(messages)
    return parse_json_markdown(response.to_dict()['choices'][0]['message']['content'])


def convert_to_note(resource: dict, retries=5):
    if retries == 0:
        return "ERROR"
    prompt = resource_to_note_template.format(resource=resource)
    messages = [
        {"role": "system", "content": "you are a program that converts structured data to natural language"},
        {"role": "user", "content": prompt}]
    response = get_openai_chatcompletion(messages, model=OPENAI_MODEL)
    return response.to_dict()['choices'][0]['message']['content']


def merge_notes(notes: list):
    notes_str = "\n- ".join(notes)
    prompt = merge_notes_template.format(notes=notes_str)
    messages = [
        {"role": "system", "content": "you are a program that compresses clinical notes"},
        {"role": "user", "content": prompt}]
    response = get_openai_chatcompletion(messages)
    return response.to_dict()['choices'][0]['message']['content']


def compress_note(note):
    prompt = summarize_input_template.format(note=note)
    messages = [
        {"role": "system", "content": "you are a program that compresses clinical notes"},
        {"role": "user", "content": prompt}]
    response = get_openai_chatcompletion(messages)
    return parse_json_markdown(response.to_dict()['choices'][0]['message']['content'])


def roundtrip_note(note):
    compressed_note = compress_note(note)
    resources = convert_to_fhir(
        note=compressed_note)
    pred_note = convert_to_note(resource=resources)
    return pred_note


def get_embedding(input_str):
    response = openai.Embedding.create(
        input=input_str, model="text-embedding-ada-002")
    return response.to_dict()['data'][0].to_dict()['embedding']


def identify_fhir_resources(note: str, resource: str):
    prompt = count_resource_template.format(note, resource)
    messages = [
        {"role": "system", "content": "you are a program that converts unstructured to structured data"},
        {"role": "user", "content": prompt}]
    response = get_openai_chatcompletion(messages)
    return parse_json_markdown(response.to_dict()['choices'][0]['message']['content'])
