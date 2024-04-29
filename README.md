# HealthSage AI LLM - from clinical note to FHIR

## Introduction

HealthSage AI's LLM's are fine-tuned versions of LLama-13b and Mixtral-8x7b to create structured information - FHIR Resources - from unstructured clinical notes - plain text.

The model is optimized to process English and/or Dutch notes and populate 10 FHIR resource types. For a full description of the scope and limitations, see the performance and limitations header below. 

## Getting started

This repository consists of the following modules:

- healthsageai.note_to_fhir.evaluation - compare generated FHIR resources against ground truth/reference resource.
- healthsageai.note_to_fhir.inference - running inference on the model, either locally or in a containerized environment.

Usage examples for both can be found in the jupyter notebooks in the docs folder.

The easiest way to get started is to run one of the Jupyter Notebooks on Google Colab and other services, e.g. for inference:

[![Open inference-note-to-fhir-colab-notebook in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/healthsage-ai/healthsage-ai-llm/blob/main/docs/inference_note_to_fhir_colab_notebook.ipynb)

## Inference: Note to FHIR

You can do Note-to-fhir inference using our NoteToFhir class:

```python
from healthsageai.note_to_fhir.inference import NoteToFhir13b, NoteToFhir8x7b
```

To run our first beta model, based on LLama-13b:
```python
model = NoteToFhir13b()
model.translate("Patient John Doe lives in Amsterdam")
```

To run our second beta model, based on LLama-8x7b:
```python
model = NoteToFhir8x7b()
model.translate("Patient Sofie de Jong woont in Amsterdam")
```


## Evaluation of accuracy

Our evaluation tool makes it easy to quantify and inspect the accuracy of generated FHIR resources w.r.t. a ground truth FHIR resource.
For that we designed the FhirScore and FhirDiff models as well as several functions to process and visualize these models. 

```python
from healthsageai.note_to_fhir.evaluation.datamodels import FhirScore, FhirDiff
from healthsageai.note_to_fhir.evaluation.utils import get_diff, diff_to_dataframe
from healthsageai.note_to_fhir.evaluation.visuals import show_diff

fhir_true, fhir_pred = load_evaluation_dataset()  # Placeholder load dataset function

diff = get_diff(fhir_true, fhir_pred, resource_type="Bundle")
show_diff(diff)
```
<img width="756" alt="image" src="https://github.com/HealthSage-AI/healthsage-ai-llm/assets/96254933/2dbdbb5a-c603-42ac-969f-7a78e00a4fde">

For a more elaborate walkthrough, see **docs/evaluation.ipynb**

## Published resources

The data sets and models are regularly published to [HuggingFace](https://huggingface.co/healthsageai).
The inference API is pushed as a Docker image to Docker Hub.

## Licensing

The code has been made available under the GNU AGPL 3.0 license. Contact HealthSage AI (hello@healthsage.ai) for commercial licensing options.

## Contributing & support

Contributions are welcome in any form! Please open an issue or a pull request. For support and discussions please visit our [Github discussions](https://github.com/HealthSage-AI/healthsage-ai-llm/discussions) or [Slack community](https://healthsageaicommunity.slack.com/).

## Validation
The current version of the Note-to-FHIR model is released as Beta for testing and development purposes only. Its not validated for clinical use. 

## Performance and limitations

### Scope of the model
This open sourced Beta model is trained within the following scope:
- FHIR R4
- 10 Resource types: 
  1. Bundle
  2. Patient
  3. Encounter
  4. Practitioner
  5. Organization
  6. Immunization
  7. Observation
  8. Condition
  9. AllergyIntolerance
  10. Procedure. 
- English language
- Dutch language (8x7b version only)

### The following features are out of scope of the current release:
- Support for Coding systems such as SNOMED CT and Loinc.
- FHIR extensions and profiles
- Any language, resource type or FHIR version not mentioned under "in scope".

We are continuously training our model and will make updates available - that address some of these items and more - on a regular basis.

### Furthermore, please note:
- **No Relative dates:** HealthSage AI Note-to-FHIR will not provide accurate FHIR datetime fields based on text that contains relative time information like "today" or "yesterday". Furthermore, relative dates like "Patient John Doe is 50 years old." will not result in an accurate birthdate estimation, since the precise birthday and -month is unknown, and since the LLM is not aware of the current date. 
- **Designed as Patient-centric:** HealthSage AI Note-to-FHIR is trained on notes describing one patient each. 
- **<4k Context window:** The training data for this application contained at most 4096 tokens. Technically the model supports of to 32k tokens.
- **Explicit Null:** If a certain FHIR element is not present in the provided text, it is explictely predicted as NULL. Explictely modeling the absence of information reduces the chance of hallucinations. 
- **Major European languages:** We've seen encouraging results on German, French, Spanish and Italian. However, these are not trained and tested on fully.
- **Uses Bundles:** For consistency and simplicity, all predicted FHIR resources are transaction Bundles.
- **Conservative estimates:** Our model is designed to stick to the information explicitely provided in the text. 
- **ID's are local:** ID fields and references are local enumerations (1,2,3, etc.). They are not yet tested on referential correctness. 
- **Generation design:** The model is designed to generate a seperate resource if there is information about that resource in the text beyond what can be described in reference fields of related resources.
- **Test results:** Our preliminary results suggest that HealthSage AI Note-to-FHIR is superior to the GPT-4 foundation model within the scope of our application in terms of FHIR Syntax and ability to replicate the original FHIR resources in our test dataset. We are currently analyzing our model on its performance for out-of-distribution data and out-of-scope data.
- **Evaluation of datetime:** Datetime values are evaluation up to the minute level, since second and sub-second timing is typically not reported in clinical notes. For applications where second or sub-second timing is relevant, we advise changing this in your evaluation.
