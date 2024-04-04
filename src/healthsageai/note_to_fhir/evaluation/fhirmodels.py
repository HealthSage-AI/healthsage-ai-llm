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

"""Contains all in-scope FHIR models for the note_to_fhir project
"""
from fhir.resources.R4B.reference import Reference
from fhir.resources.R4B.patient import (
    Patient,
    PatientCommunication,
    PatientContact,
    PatientLink,
)
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.encounter import Encounter, EncounterParticipant, EncounterHospitalization, EncounterLocation, EncounterDiagnosis
from fhir.resources.R4B.allergyintolerance import AllergyIntolerance, AllergyIntoleranceReaction
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.narrative import Narrative
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.bundle import Bundle, BundleEntry
from fhir.resources.R4B.organization import Organization, OrganizationContact
from fhir.resources.R4B.practitioner import Practitioner
from fhir.resources.R4B.procedure import Procedure, ProcedurePerformer
from fhir.resources.R4B.condition import Condition
from fhir.resources.R4B.immunization import Immunization, ImmunizationProtocolApplied
from fhir.resources.R4B.observation import Observation, ObservationComponent
from fhir.resources.R4B.medication import Medication
from fhir.resources.R4B.quantity import Quantity
from fhir.resources.R4B.resource import Resource
from fhir.resources.R4B.extension import Extension

object_mapping = {
    "Patient": Patient,
    "PatientCommunication": PatientCommunication,
    "PatientContact": PatientContact,
    "PatientLink": PatientLink,
    "Address": Address,
    "CodeableConcept": CodeableConcept,
    "Coding": Coding,
    "HumanName": HumanName,
    "ContactPoint": ContactPoint,
    "Encounter": Encounter,
    "EncounterParticipant": EncounterParticipant,
    "AllergyIntolerance": AllergyIntolerance,
    "Period": Period,
    "Narrative": Narrative,
    "Identifier": Identifier,
    "Bundle": Bundle,
    "BundleEntry": BundleEntry,
    "Organization": Organization,
    "Practitioner": Practitioner,
    "Procedure": Procedure,
    "Condition": Condition,
    "Immunization": Immunization,
    "Observation": Observation,
    "Medication": Medication,
    "Reference": Reference,
    "Quantity": Quantity,
    "Resource": Resource,
    "AllergyIntoleranceReaction": AllergyIntoleranceReaction,
    "ProcedurePerformer": ProcedurePerformer,
    "ImmunizationProtocolApplied": ImmunizationProtocolApplied,
    "ObservationComponent": ObservationComponent,
    "EncounterHospitalization": EncounterHospitalization,
    "EncounterLocation": EncounterLocation,
    "OrganizationContact": OrganizationContact,
    "EncounterDiagnosis": EncounterDiagnosis,
    "Extension": Extension,
}
