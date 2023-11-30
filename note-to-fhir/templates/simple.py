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


unique_resource_template = """Generate a HL7 FHIR R4 resource of type {resource}. \n 
Instructions: \n 
1. Filter out what information in the clinical note is relevant for the FHIR resource {resource}.\n
2. If there is no information that relates to {resource}, return an empty json string.
3. Else, convert the information into FHIR R4 format of type {resource}.
4. Only put in information that is explicitely mentioned in the note. Do not put placeholder values for things like birthdates and/or addresses.
5. If there are multiple elements of a resource needed, put them in an array.
6. Return the result in an array json string. denote the start and end of the json with a  markdown codeblock ```json ``` \n
\n
Here is the clinical note:
\nBEGIN NOTE\n{note}. \nEND NOTE \n\nOutput the FHIR R4. Formatted note as a clean valid JSON string without newlines, tabs or spaces.
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

merge_notes_template = """
Goal: combine the following clinical notes into a single note that a healthcare professional could've made. 
Details:
- merge information that is clearly duplicated
- make it one consistent whole

Notes:
{notes}

"""

chunk_input_note_template = """
Goal: split the following clinical note in to smaller subnotes that can be processed in parallel. 
Instructions:
1. Each subnote should be self-contained, meaning:
    - There is no context missing
    - Things like patient reference and date reference are included in each subnote.
2. Return the note in an array of json strings in a markdown codeblock. 
    - each json string describes one subnote
    - each json string can be different, but is self-contained.

About 3-10 chunks should do the trick.

Here is the original note:
{note}

"""


summarize_input_template = """
Goal: convert the following clinical note into a compact json. 

Here is the note:
{note}

Return the result in a json string. denote the start and end of the json with a  markdown codeblock 
```json 
[JSON STRING HERE]
``` 

Make the json string as short as possible, without omitting any information.
"""

FHIR_mapping_template = """
Goal: map the following clinical note into FHIR R4 on resource level. 
The possible FHIR resources are 'Patient', 'Condition', 'Encounter', 'CarePlan',
'Medication','Observation','Medication' and 'Procedure'.

Here is the note:
{note}

Return the result in a json string. denote the start and end of the json with a  markdown codeblock.
The keys of the dictionaries correspond to FHIR resource types and the values correspond to text fragments from the clinical note.
Example output:
```json 
{"Patient" : "John Doe", "Condition" : ["Diabetes","fever"], "Medication": "Insulin", "Observation": "full-time employed"}
``` 

Make the json string as short as possible, without omitting any information.
"""
