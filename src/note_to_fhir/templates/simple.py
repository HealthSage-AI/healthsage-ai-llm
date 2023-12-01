template = """Translate the following clinical note into HL7 FHIR R4 Format. 
instructions: 
- Do not insert any values that are not in the note. 
- Do not infer or impute any values
- Only include information that is essential:
    - information that is in the clinical note
    - information that is mandatory for a valid FHIR resource.
Here is the note:
{note}
Return the result in an array of json string. denote the start and end of the json with a markdown codeblock:
```json 
[RESOURCE HERE]
```
"""


llama_template = """[INST] <<SYS>>
INSTRUCTION
Translate the following clinical note into HL7 FHIR R4 Format. 
- Do not insert any values that are not in the note. 
- Do not infer or impute any values
- Only include information that is essential:
    - information that is in the clinical note
    - information that is mandatory for a valid FHIR resource.

OUTPUT FORMAT
Return the HL7 FHIR structured information as a json string. denote the start and end of the json with a markdown codeblock:
```json 
[RESOURCE HERE]
```
<</SYS>>

CLINICAL NOTE
{note}

[/INST]
"""

resource_to_note_template = """
Goal: Convert the following JSON file describing a HL7 FHIR R4 Resource to a clinical note.

Resource: 
{resource}

Details:
- Don't mention ID's, coding concepts or other FHIR related artifacts.
- Explicitely describe all of the information in the resource, including the relationship between resources.
- Datetime fields that are converted to text should still include timezone information and should include seconds.
- Don't use placeholders/imputation
- Don't ask follow-up questions, just convert the resource to human-readible text.
- Information that has the value 'unknown' in the resource don't have to be converted to text.
- {custom_detail_1}
- {custom_detail_2}
- {custom_detail_3}
"""