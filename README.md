# HealthSage AI LLM - from clinical note to FHIR

## Introduction

HealthSage AI LLM is a fine-tuned version of Meta's Llama 2 13B to create structured information - FHIR Resources - from
unstructured clinical notes - plain text.

It leverages the synthetic patient data generator [Synthea](https://synthetichealth.github.io/synthea/) to generate
the clinical notes as well as the paired FHIR Resources. Other datasets are in the works.

The following FHIR R4 Resources are currently supported and validated:

Patient
Encounter
Organization
Location
Practitioner
Condition
Procedure
Observation
AllergyIntolerance
Immunization

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

The data sets and models are regularly published to HuggingFace.
The inference API is pushed as a Docker image to Docker Hub.

### Licensing

The code has been made available under the AGPL 3.0 license. Contact HealthSage AI (info@healthsage.ai) for commercial licensing options.

### Contributing

Contributions are welcome in any form! Please open an issue or a pull request.

### Validation

A validation report for our latest model is available here: TODO.
