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
from src.note_to_fhir.data_utils import drop_snomed_loinc, drop_nones
from src.note_to_fhir.templates.simple import template_dict
from src.note_to_fhir.parsers import parse_note_to_fhir

class NoteToFhir(object):

    def __init__(self, model_name: str, adapter_name: str, template_style: str) -> None:
        """_summary_

        Args:
            model_name (str or os.PathLike): The base model
            adapter_name (str or os.PathLike): The Q-LoRA adapter
            template_style (str): "gpt", "llama" or "mixtral"
        """
        self.template = template_dict[template_style]
        bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            quantization_config=bnb_config,
            device_map='auto',
        )

        model.config.use_cache = False
        model.load_adapter(adapter_name)

        tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, return_tensor="pt", padding=True)
        tokenizer.pad_token = tokenizer.bos_token
        tokenizer.padding_side = 'right'

        self.generator = pipeline(
            model=model, 
            tokenizer=tokenizer,
            task="text-generation",
            do_sample=True,
            eos_token_id=model.config.eos_token_id,
            max_length=4096
        )

    def translate(self, note : str) -> dict:
        """Convert a note to FHIR

        Args:
            note (str): clinical note
        """
        prompt = self.template.format(note=note)
        generated_output = self.generator(prompt)
        fhir = parse_note_to_fhir(generated_output[0]['generated_text'])
        fhir = drop_nones(fhir)
        fhir = drop_snomed_loinc(fhir)
        return fhir
    
class NoteToFhir13b(NoteToFhir):

    def __init__(self):
        super().__init__(model_name="meta-llama/Llama-2-13b-chat-hf",
                        adapter_name="healthsageai/note-to-fhir-13b-adapter",
                        template_style="llama")
        
class NoteToFhir8x7b(NoteToFhir):

    def __init__(self):
        super().__init__(model_name="mistralai/Mixtral-8x7B-Instruct-v0.1",
                        adapter_name="healthsageai/note-to-fhir-8x7b-mixtral-dev",
                        template_style="mixtral")