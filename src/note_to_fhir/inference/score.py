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

from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import json
import os
from templates.simple import llama_template as template

MODEL_NAME = "meta-llama/Llama-2-13b-chat-hf"
ADAPTER_NAME = "healthsageai/note-to-fhir-13b-adapter"

def model_path(name: str) -> str:
    return os.path.join(os.getenv("AZUREML_MODEL_DIR"), "models", name)


def init():
    global generator

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_path(MODEL_NAME),
        trust_remote_code=True,
        quantization_config=bnb_config,
        device_map='auto',
    )

    model.config.use_cache = False
    model.load_adapter(model_path(ADAPTER_NAME))

    tokenizer = AutoTokenizer.from_pretrained(model_path(MODEL_NAME), trust_remote_code=True, return_tensor="pt", padding=True)
    tokenizer.pad_token = tokenizer.bos_token
    tokenizer.padding_side = 'right'

    generator = pipeline(
        model=model, 
        tokenizer=tokenizer,
        task="text-generation",
        do_sample=True,
        eos_token_id=model.config.eos_token_id,
        max_length=4096
    )

def run(raw_data: str) -> str:
    global generator

    # TODO: Validate this
    message = json.loads(raw_data)["message"]
    message_in_template = template.format(note=message)

    generated_output = generator(message_in_template)
    # TODO: Validate this
    fhir_json = generated_output[0]['generated_text'].split("```")[3][4:].strip(" \t\n\r")

    return json.loads(fhir_json)
