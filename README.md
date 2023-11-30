# HealthSage AI LLM - from clinical note to FHIR

## Introduction

HealthSage AI's LLM is a fine-tuned version of Meta's Llama 2 13B to create structured information - FHIR Resources - from
unstructured clinical notes - plain text.

The model is optimized to process english notes and populate 10 FHIR resource types. For a full description of the scope and limitations, see the performance and limitations header below. 

## Getting started

This repository consists of the following modules:

- training_evaluation - all scripts that have been used to train the model and specifically validate the FHIR Resource
  validity.
- inference - running inference on the model, either locally or in a containerized environment.
- demo - a simple demo of the system, using a docker-compose setup.

The easiest way to get started is run one of the Jupyter Notebooks on Google Colab and other services, e.g. for inference:

- ./inference/healthsage-llm-13b.ipynb

A second step could be to deploy the starter kit for an end to end demo of the system: `docker compose -p starter-kit up`.
A decent GPU is required for this step.

Lastly, you could fine-tune the model on your own data by modifying the training scripts and running them on a GPU.

## Published resources

The data sets and models are regularly published to [HuggingFace](https://huggingface.co/healthsageai).
The inference API is pushed as a Docker image to Docker Hub.

## Licensing

The code has been made available under the AGPL 3.0 license. Contact HealthSage AI (hello@healthsage.ai) for commercial licensing options.

## Contributing

Contributions are welcome in any form! Please open an issue or a pull request.

## Validation
The current version of the Note-to-FHIR model is for testing and development purposes only. Its not validated for clinical use. 

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


### The following features are out of scope of the current release:
- Support for Coding systems such as SNOMED CT and Loinc.
- FHIR extensions and profiles
- Any language, resource type or FHIR version not mentioned under "in scope". 

### Furthermore, please note:
- **No Relative dates:** HealthSage AI Note-to-FHIR will not provide accurate FHIR datetime fields based on text that contains relative time information like "today" or "yesterday". Furthermore, relative dates like "Patient John Doe is 50 years old." will not result in an accurate birthdate estimation, since the precise birthday and -month is unknown, and since the LLM is not aware of the current date. 
- **Designed as Patient-centric:** HealthSage AI Note-to-FHIR is trained on notes describing one patient each. 
- **<4k Context window:** The training data for this application contained at most 3686 tokens, which is 90% of the context window for Llama-2 (4096)
- **Explicit Null:** If a certain FHIR element is not present in the provided text, it is explicitely predicted as NULL. Explicitely modeling the absence of information reduces the chance of hallucinations. 
- **Uses Bundles:** For consistency and simplicity, all predicted FHIR resources are Bundled.
- **Conservative estimates:** Our model is designed to stick to the information explicitely provided in the text. 
- **ID's are local:** ID fields and references are local enumarations (1,2,3, etc.). They are not yet tested on referential correctness. 
- **Generation design:** The model is designed to generate a seperate resource if there is information about that resource in the text beyond what can be described in reference fields of related resources.
- **This Beta application is still in early development:** Our preliminary results suggest that HealthSage AI Note-to-FHIR is superior to the GPT-4 foundation model within the scope of our application in terms of Fhir Syntax and ability to replicate the original FHIR resources in our test dataset. However, our model is still being analyzed on its performance for out-of-distribution data and out-of-scope data.

## Future updates
The current version is tested for English. In future updates we will support additional languages, FHIR resources, and terminologies.
