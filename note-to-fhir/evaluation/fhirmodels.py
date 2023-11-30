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

from pydantic import BaseModel, Field
from typing import Optional


class ElementAssessmentModel(BaseModel):

    name: str
    required: bool = False
    # "fixed", "compare_string", "any"
    expected_value_assessment: Optional[str] = None
    expected_value: Optional[str] = None
    ignore: bool = Field(default=False)
    expected_reference_value: Optional[str] = None  # e.g. "Patient.name"


class PatientAssessmentModel(BaseModel):
    resourceType = ElementAssessmentModel(
        name="resourceType", required=True, expected_value="Patient")
    id = ElementAssessmentModel(
        name="id", required=True, expected_value_assessment="any")
    identifier = ElementAssessmentModel(
        name="identifier", required=False, expected_value_assessment="compare_string", ignore=True)
    active = ElementAssessmentModel(
        name="active", required=False, expected_value_assessment="compare_string")
    name = ElementAssessmentModel(
        name="name", required=False, expected_value_assessment="compare_string")
    telecom = ElementAssessmentModel(
        name="telecom", required=False, expected_value_assessment="compare_string")
    gender = ElementAssessmentModel(
        name="gender", required=False, expected_value_assessment="compare_string")
    birthDate = ElementAssessmentModel(
        name="birthDate", required=False, expected_value_assessment="compare_string")
    deceased = ElementAssessmentModel(
        name="deceased", required=False, expected_value_assessment="compare_string")
    address = ElementAssessmentModel(
        name="address", required=False, expected_value_assessment="compare_string")
    photo = ElementAssessmentModel(
        name="photo", required=False, expected_value_assessment="compare_string", ignore=True)
    maritalStatus = ElementAssessmentModel(
        name="maritalStatus", required=False, expected_value_assessment="compare_string")
    multipleBirthBoolean = ElementAssessmentModel(
        name="multipleBirthBoolean", required=False, expected_value_assessment="compare_string")
    multipleBirthInteger = ElementAssessmentModel(
        name="multipleBirthInteger", required=False, expected_value_assessment="compare_string")
    contact = ElementAssessmentModel(
        name="contact", required=False, expected_value_assessment="compare_string")
    communication = ElementAssessmentModel(
        name="communication", required=False, expected_value_assessment="compare_string")
    generalPractitioner = ElementAssessmentModel(
        name="generalPractitioner", required=False, expected_value_assessment="compare_string")
    managingOrganization = ElementAssessmentModel(
        name="managingOrganization", required=False, expected_value_assessment="compare_string")
    link = ElementAssessmentModel(
        name="link", required=False, expected_value_assessment="compare_string", ignore=True)


class EncounterAssessmentModel(BaseModel):
    resourceType = ElementAssessmentModel(
        name="resourceType", required=True, expected_value="Encounter")
    id = ElementAssessmentModel(
        name="id", required=True, expected_value_assessment="any")
    status = ElementAssessmentModel(
        name="status", required=True, expected_value_assessment="compare_string")
    class_ = ElementAssessmentModel(
        name="class", required=False, expected_value_assessment="compare_string")
    priority = ElementAssessmentModel(
        name="priority", required=False, expected_value_assessment="compare_string")
    type_ = ElementAssessmentModel(
        name="type", required=False, expected_value_assessment="compare_string")
    serviceType = ElementAssessmentModel(
        name="serviceType", required=False, expected_value_assessment="compare_string")
    subject = ElementAssessmentModel(
        name="subject", required=False, expected_value_assessment="any")
    participant = ElementAssessmentModel(
        name="participant", required=False, expected_value_assessment="any")
    appointment = ElementAssessmentModel(
        name="appointment", required=False, expected_value_assessment="compare_string")
    period = ElementAssessmentModel(
        name="period", required=False, expected_value_assessment="compare_string")
    length = ElementAssessmentModel(
        name="length", required=False, expected_value_assessment="compare_string")
    reason = ElementAssessmentModel(
        name="reason", required=False, expected_value_assessment="compare_string")
    length = ElementAssessmentModel(
        name="length", required=False, expected_value_assessment="compare_string")
    reasonCode = ElementAssessmentModel(
        name="reasonCode", required=False, expected_value_assessment="compare_coding")
    reasonReference = ElementAssessmentModel(
        name="reasonReference", required=False, expected_value_assessment="any")
    diagnosis = ElementAssessmentModel(
        name="diagnosis", required=False, expected_value_assessment="compare_string")
    account = ElementAssessmentModel(
        name="account", required=False, expected_value_assessment="compare_string")
    location = ElementAssessmentModel(
        name="location", required=False, expected_value_assessment="compare_string")
    admission = ElementAssessmentModel(
        name="admission", required=False, expected_value_assessment="compare_string")
    specialCourtesy = ElementAssessmentModel(
        name="specialCourtesy", required=False, expected_value_assessment="compare_string")
    specialArrangement = ElementAssessmentModel(
        name="specialArrangement", required=False, expected_value_assessment="compare_string")
    dietPreference = ElementAssessmentModel(
        name="dietPreference", required=False, expected_value_assessment="compare_string")
    actualPeriod = ElementAssessmentModel(
        name="actualPeriod", required=False, expected_value_assessment="compare_string")
    plannedStartDate = ElementAssessmentModel(
        name="plannedStartDate", required=False, expected_value_assessment="compare_string")
    plannedEndDate = ElementAssessmentModel(
        name="plannedEndDate", required=False, expected_value_assessment="compare_string")
    virtualService = ElementAssessmentModel(
        name="virtualService", required=False, expected_value_assessment="compare_string")
    serviceProvider = ElementAssessmentModel(
        name="serviceProvider", required=False, expected_value_assessment="compare_string")
    partOf = ElementAssessmentModel(
        name="partOf", required=False, expected_value_assessment="any")
    careTeam = ElementAssessmentModel(
        name="careTeam", required=False, expected_value_assessment="compare_string")
    basedOn = ElementAssessmentModel(
        name="basedOn", required=False, expected_value_assessment="any")
    episodeOfCare = ElementAssessmentModel(
        name="episodeOfCare", required=False, expected_value_assessment="any")
    subjectStatus = ElementAssessmentModel(
        name="subjectStatus", required=False, expected_value_assessment="compare_string")


class OrganizationAssessmentModel(BaseModel):
    resourceType = ElementAssessmentModel(
        name="resourceType", required=False, expected_value="Organization")
    active = ElementAssessmentModel(
        name="active", required=False, expected_value_assessment="compare_string")
    type_ = ElementAssessmentModel(
        name="type", required=False, expected_value_assessment="compare_string")
    name = ElementAssessmentModel(
        name="name", required=False, expected_value_assessment="compare_string")
    alias = ElementAssessmentModel(
        name="alias", required=False, expected_value_assessment="compare_string")
    description = ElementAssessmentModel(
        name="description", required=False, expected_value_assessment="any")
    contact = ElementAssessmentModel(
        name="contact", required=False, expected_value_assessment="compare_string")
    partof = ElementAssessmentModel(
        name="partof", required=False, expected_value_assessment="any")
    endpoint = ElementAssessmentModel(
        name="endpoint", required=False, expected_value_assessment="any", ignore=True)
    qualification = ElementAssessmentModel(
        name="qualification", required=False, expected_value_assessment="any", ignore=True)


class LocationAssessmentModel(BaseModel):
    resourceType = ElementAssessmentModel(
        name="resourceType", required=False, expected_value="Location")
    identifier = ElementAssessmentModel(
        name="identifier", required=False, expected_value_assessment="compare_string", ignore=True)
    status = ElementAssessmentModel(
        name="status", required=False, expected_value_assessment="compare_string")
    operationalStatus = ElementAssessmentModel(
        name="operationalStatus", required=False, expected_value_assessment="compare_string")
    name = ElementAssessmentModel(
        name="name", required=False, expected_value_assessment="compare_string")
    alias = ElementAssessmentModel(
        name="alias", required=False, expected_value_assessment="compare_string", ignore=True)
    description = ElementAssessmentModel(
        name="description", required=False, expected_value_assessment="any")


class PractitionerAssessmentModel(BaseModel):
    resourceType = ElementAssessmentModel(
        name="resourceType", required=False, expected_value="Practitioner")
    id = ElementAssessmentModel(
        name="id", required=False, expected_value_assessment="any")
    identifier = ElementAssessmentModel(
        name="identifier", required=False, expected_value_assessment="compare_string", ignore=True)
    active = ElementAssessmentModel(
        name="active", required=False, expected_value_assessment="compare_string")
    name = ElementAssessmentModel(
        name="name", required=False, expected_value_assessment="compare_string")
    telecom = ElementAssessmentModel(
        name="telecom", required=False, expected_value_assessment="compare_string")
    gender = ElementAssessmentModel(
        name="gender", required=False, expected_value_assessment="compare_string")
    birthDate = ElementAssessmentModel(
        name="birthDate", required=False, expected_value_assessment="compare_string")
    deceased = ElementAssessmentModel(
        name="deceased", required=False, expected_value_assessment="compare_string")
    address = ElementAssessmentModel(
        name="address", required=False, expected_value_assessment="compare_string")
    photo = ElementAssessmentModel(
        name="photo", required=False, expected_value_assessment="compare_string", ignore=True)
    qualification = ElementAssessmentModel(
        name="qualification", required=False, expected_value_assessment="any", ignore=True)
    communication = ElementAssessmentModel(
        name="communication", required=False, expected_value_assessment="compare_string")


class ConditionAssessmentModel(BaseModel):
    resourceType = ElementAssessmentModel(
        name="resourceType", required=True, expected_value="Condition")
    clinicalStatus = ElementAssessmentModel(
        name="clinicalStatus", required=True, expected_value_assessment="compare_string")
    verificationStatus = ElementAssessmentModel(
        name="verificationStatus", required=False, expected_value_assessment="compare_string")
    category = ElementAssessmentModel(
        name="category", required=False, expected_value_assessment="compare_string")
    severity = ElementAssessmentModel(
        name="severity", required=False, expected_value_assessment="compare_string")
    code = ElementAssessmentModel(
        name="code", required=True, expected_value_assessment="compare_coding")
    bodySite = ElementAssessmentModel(
        name="bodySite", required=False, expected_value_assessment="compare_coding")
    subject = ElementAssessmentModel(
        name="subject", required=True, expected_value_assessment="any")
    encounter = ElementAssessmentModel(
        name="encounter", required=False, expected_value_assessment="compare_string")
    onsetDateTime = ElementAssessmentModel(
        name="onsetDateTime", required=False, expected_value_assessment="compare_string")
    onsetAge = ElementAssessmentModel(
        name="onsetAge", required=False, expected_value_assessment="compare_string")
    onsetPeriod = ElementAssessmentModel(
        name="onsetPeriod", required=False, expected_value_assessment="compare_string")
    onsetRange = ElementAssessmentModel(
        name="onsetRange", required=False, expected_value_assessment="compare_string")
    onsetString = ElementAssessmentModel(
        name="onsetString", required=False, expected_value_assessment="compare_string")
    abatementDateTime = ElementAssessmentModel(
        name="abatementDateTime", required=False, expected_value_assessment="compare_string")
    abatementAge = ElementAssessmentModel(
        name="abatementAge", required=False, expected_value_assessment="compare_string")
    abatementRange = ElementAssessmentModel(
        name="abatementRange", required=False, expected_value_assessment="compare_string")
    abatementString = ElementAssessmentModel(
        name="abatementString", required=False, expected_value_assessment="compare_string")
    recordedDate = ElementAssessmentModel(
        name="recordedDate", required=False, expected_value_assessment="compare_string")
    participant = ElementAssessmentModel(
        name="participant", required=False, expected_value_assessment="any")
    stage = ElementAssessmentModel(
        name="stage", required=False, expected_value_assessment="compare_string")
    evidence = ElementAssessmentModel(
        name="evidence", required=False, expected_value_assessment="compare_coding")
    note = ElementAssessmentModel(
        name="note", required=False, expected_value_assessment="compare_string")


class ProcedureAssessmentModel(BaseModel):

    resourceType = ElementAssessmentModel(name="resourceType", required=True, expected_value="Procedure")
    partOf = ElementAssessmentModel(
        name="partOf", required=False, expected_value_assessment="compare_string")
    status = ElementAssessmentModel(
        name="status", required=True, expected_value_assessment="compare_string")
    statusReason = ElementAssessmentModel(
        name="statusReason", required=False, expected_value_assessment="compare_coding")
    category = ElementAssessmentModel(
        name="category", required=False,expected_value_assessment="compare_coding")
    code = ElementAssessmentModel(
        name="code", required=True, expected_value_assessment="compare_coding")
    subject = ElementAssessmentModel(
        name="subject", required=True, expected_value_assessment="any")
    focus = ElementAssessmentModel(
        name="focus", required=False, expected_value_assessment="compare_string")
    encounter = ElementAssessmentModel(
        name="encounter", required=False, expected_value_assessment="any")
    recorded = ElementAssessmentModel(
        name="recorded", required=False, expected_value_assessment="compare_string")
    recorder = ElementAssessmentModel(
        name="recorder", required=False, expected_value_assessment="compare_string")
    reportedBoolean = ElementAssessmentModel(
        name="reportedBoolean", required=False, expected_value_assessment="compare_string")
    reportedReference = ElementAssessmentModel(
        name="reportedReference", required=False, expected_value_assessment="compare_string")
    performer = ElementAssessmentModel(
        name="performer", required=False, expected_value_assessment="any")
    location = ElementAssessmentModel(
        name="location", required=False, expected_value_assessment="compare_string")
    reasonCode = ElementAssessmentModel(
        name="reasonCode", ignore=False, required=False, expected_value_assessment="compare_coding")
    reasonReference = ElementAssessmentModel(
        name="reasonReference", required=False, expected_value_assessment="compare_string")
    bodySite = ElementAssessmentModel(
        name="bodySite", ignore=False, required=False, expected_value_assessment="compare_coding")
    outcome = ElementAssessmentModel(
        name="outcome", required=False, ignore=False, expected_value_assessment="compare_coding")
    report = ElementAssessmentModel(
        name="report", required=False, expected_value_assessment="compare_string")
    complication = ElementAssessmentModel(
        name="complication", required=False, ignore=False, expected_value_assessment="compare_coding")
    followUp = ElementAssessmentModel(
        name="followUp", required=False, expected_value_assessment="compare_string")
    note = ElementAssessmentModel(
        name="note", required=False, expected_value_assessment="compare_string")
    focalDevice = ElementAssessmentModel(
        name="focalDevice", required=False, expected_value_assessment="compare_string")
    used = ElementAssessmentModel(
        name="used", required=False, expected_value_assessment="compare_string")
    supportingInfo = ElementAssessmentModel(
        name="supportingInfo", required=False, expected_value_assessment="compare_string")


class ObservationAssessmentModel(BaseModel):
    resourceType = ElementAssessmentModel(
        name="resourceType", required=True, expected_value="Observation")
    id = ElementAssessmentModel(
        name="id", required=True, expected_value_assessment="any")
    triggeredBy = ElementAssessmentModel(
        name="triggeredBy", required=False, expected_value_assessment="compare_string")
    partOf = ElementAssessmentModel(
        name="partOf", required=False, expected_value_assessment="compare_string")
    status = ElementAssessmentModel(
        name="status", required=True, expected_value_assessment="compare_string")
    category = ElementAssessmentModel(
        name="category", required=False, expected_value_assessment="compare_string")
    code = ElementAssessmentModel(
        name="code", required=True, expected_value_assessment="compare_coding")
    subject = ElementAssessmentModel(
        name="subject", required=True, expected_value_assessment="any")
    focus = ElementAssessmentModel(
        name="focus", required=False, expected_value_assessment="compare_string")
    encounter = ElementAssessmentModel(
        name="encounter", required=False, expected_value_assessment="compare_string")
    effectiveDateTime = ElementAssessmentModel(
        name="effectiveDateTime", required=False, expected_value_assessment="compare_string")
    effectivePeriod = ElementAssessmentModel(
        name="effectivePeriod", required=False, expected_value_assessment="compare_string")
    effectiveTiming = ElementAssessmentModel(
        name="effectiveTiming", required=False, expected_value_assessment="compare_string")
    effectiveInstant = ElementAssessmentModel(
        name="effectiveInstant", required=False, expected_value_assessment="compare_string")
    issued = ElementAssessmentModel(
        name="issued", required=False, expected_value_assessment="compare_string")
    performer = ElementAssessmentModel(
        name="performer", required=False, expected_value_assessment="any")
    valueQuantity = ElementAssessmentModel(
        name="valueQuantity", required=False, expected_value_assessment="compare_string")
    valueCodeableConcept = ElementAssessmentModel(
        name="valueCodeableConcept", required=False, expected_value_assessment="compare_string")
    valueString = ElementAssessmentModel(
        name="valueString", required=False, expected_value_assessment="compare_string")
    valueBoolean = ElementAssessmentModel(
        name="valueBoolean", required=False, expected_value_assessment="compare_string")
    valueInteger = ElementAssessmentModel(
        name="valueInteger", required=False, expected_value_assessment="compare_string")
    valueRange = ElementAssessmentModel(
        name="valueRange", required=False, expected_value_assessment="compare_string")
    valueRatio = ElementAssessmentModel(
        name="valueRatio", required=False, expected_value_assessment="compare_string")
    valueSampledData = ElementAssessmentModel(
        name="valueSampledData", required=False, expected_value_assessment="compare_string")
    valueTime = ElementAssessmentModel(
        name="valueTime", required=False, expected_value_assessment="compare_string")
    valueDateTime = ElementAssessmentModel(
        name="valueDateTime", required=False, expected_value_assessment="compare_string")
    valuePeriod = ElementAssessmentModel(
        name="valuePeriod", required=False, expected_value_assessment="compare_string")
    valueAttachment = ElementAssessmentModel(
        name="valueAttachment", required=False, expected_value_assessment="compare_string")
    valueReference = ElementAssessmentModel(
        name="valueReference", required=False, expected_value_assessment="compare_string")
    dataAbsentReason = ElementAssessmentModel(
        name="dataAbsentReason", required=False, expected_value_assessment="compare_string")
    interpretation = ElementAssessmentModel(
        name="interpretation", required=False, expected_value_assessment="compare_string")
    note = ElementAssessmentModel(
        name="note", required=False, expected_value_assessment="compare_string")
    bodySite = ElementAssessmentModel(
        name="bodySite", required=False, expected_value_assessment="compare_coding")
    bodyStructure = ElementAssessmentModel(
        name="bodyStructure", required=False, expected_value_assessment="compare_coding")
    method = ElementAssessmentModel(
        name="method", required=False, expected_value_assessment="compare_string")
    specimen = ElementAssessmentModel(
        name="specimen", required=False, expected_value_assessment="compare_string")
    device = ElementAssessmentModel(
        name="device", required=False, expected_value_assessment="compare_string")
    referenceRange = ElementAssessmentModel(
        name="referenceRange", required=False, expected_value_assessment="compare_string")
    hasMember = ElementAssessmentModel(
        name="hasMember", required=False, expected_value_assessment="compare_string")
    derivedFrom = ElementAssessmentModel(
        name="derivedFrom", required=False, expected_value_assessment="compare_string")
    component = ElementAssessmentModel(
        name="component", required=False, expected_value_assessment="compare_string")


class AllergyIntoleranceAssessmentModel(BaseModel):

    resourceType = ElementAssessmentModel(
        name="resourceType", required=True, expected_value="AllergyIntolerance")
    clinicalStatus = ElementAssessmentModel(
        name="clinicalStatus", required=True, expected_value_assessment="compare_string")
    verificationStatus = ElementAssessmentModel(
        name="verificationStatus", required=False, expected_value_assessment="compare_string")
    _type = ElementAssessmentModel(
        name="type", required=False, expected_value_assessment="compare_string")
    category = ElementAssessmentModel(
        name="category", required=False, expected_value_assessment="compare_string")
    criticality = ElementAssessmentModel(
        name="criticality", required=False, expected_value_assessment="compare_string")
    code = ElementAssessmentModel(
        name="code", required=False, expected_value_assessment="compare_coding")
    patient = ElementAssessmentModel(
        name="patient", required=False, expected_value_assessment="any")
    encounter = ElementAssessmentModel(
        name="encounter", required=False, expected_value_assessment="any")
    onsetDateTime = ElementAssessmentModel(
        name="onsetDateTime", required=False, expected_value_assessment="compare_string")
    onsetAge = ElementAssessmentModel(
        name="onsetAge", required=False, expected_value_assessment="compare_string")
    onsetPeriod = ElementAssessmentModel(
        name="onsetPeriod", required=False, expected_value_assessment="compare_string")
    onsetRange = ElementAssessmentModel(
        name="onsetRange", required=False, expected_value_assessment="compare_string")
    onsetString = ElementAssessmentModel(
        name="onsetString", required=False, expected_value_assessment="compare_string")
    recordedDate = ElementAssessmentModel(
        name="recordedDate", required=False, expected_value_assessment="compare_string")
    participant = ElementAssessmentModel(
        name="participant", required=False, expected_value_assessment="compare_string")
    lastOccurrence = ElementAssessmentModel(
        name="lastOccurrence", required=False, expected_value_assessment="compare_string")
    note = ElementAssessmentModel(
        name="note", required=False, expected_value_assessment="compare_string")
    reaction = ElementAssessmentModel(
        name="reaction", required=False, expected_value_assessment="compare_string")


class ImmunizationAssessmentModel(BaseModel):
    resourceType = ElementAssessmentModel(
        name="resourceType", required=True, expected_value="Immunization")
    id = ElementAssessmentModel(name="id", required=True, expected_value_assessment="any")
    basedOn = ElementAssessmentModel(
        name="basedOn", required=False, expected_value_assessment="any")
    status = ElementAssessmentModel(
        name="status", required=False, expected_value_assessment="compare_string")
    statusReason = ElementAssessmentModel(
        name="statusReason", required=False, expected_value_assessment="compare_string")
    vaccineCode = ElementAssessmentModel(
        name="vaccineCode", required=False, expected_value_assessment="compare_string")
    administeredProduct = ElementAssessmentModel(
        name="administeredProduct", required=False, expected_value_assessment="compare_string")
    manufacturer = ElementAssessmentModel(
        name="manufacturer", required=False, expected_value_assessment="compare_string")
    lotNumber = ElementAssessmentModel(
        name="lotNumber", required=False, expected_value_assessment="compare_string")
    vaccinationDate = ElementAssessmentModel(
        name="vaccinationDate", required=False, expected_value_assessment="compare_string")
    expirationDate = ElementAssessmentModel(
        name="expirationDate", required=False, expected_value_assessment="compare_string")
    patient = ElementAssessmentModel(
        name="patient", required=False, expected_value_assessment="any")
    encounter = ElementAssessmentModel(
        name="encounter", required=False, expected_value_assessment="any")
    supportingInformation = ElementAssessmentModel(
        name="supportingInformation", required=False, expected_value_assessment="compare_string")
    occurrenceDateTime = ElementAssessmentModel(
        name="occurrenceDateTime", required=False, expected_value_assessment="compare_string")
    occurenceString = ElementAssessmentModel(
        name="occurenceString", required=False, expected_value_assessment="compare_string")
    primarySource = ElementAssessmentModel(
        name="primarySource", required=False, expected_value_assessment="compare_string")
    informationSource = ElementAssessmentModel(
        name="informationSource", required=False, expected_value_assessment="compare_string")
    location = ElementAssessmentModel(
        name="location", required=False, expected_value_assessment="compare_string")
    site = ElementAssessmentModel(
        name="site", required=False, expected_value_assessment="compare_string")
    route = ElementAssessmentModel(
        name="route", required=False, expected_value_assessment="compare_string")
    doseQuantity = ElementAssessmentModel(
        name="doseQuantity", required=False, expected_value_assessment="compare_string")
    performer = ElementAssessmentModel(
        name="performer", required=False, expected_value_assessment="compare_string")
    note = ElementAssessmentModel(
        name="note", required=False, expected_value_assessment="compare_string")
    reason = ElementAssessmentModel(
        name="reason", required=False, expected_value_assessment="compare_string")
    isSubpotent = ElementAssessmentModel(
        name="isSubpotent", required=False, expected_value_assessment="compare_string")
    subPotentReason = ElementAssessmentModel(
        name="subPotentReason", required=False, expected_value_assessment="compare_string")
    programEligibility = ElementAssessmentModel(
        name="programEligibility", required=False, expected_value_assessment="compare_string")
    fundingSource = ElementAssessmentModel(
        name="fundingSource", required=False, expected_value_assessment="compare_string")
    reaction = ElementAssessmentModel(
        name="reaction", required=False, expected_value_assessment="compare_string")
    protocolApplied = ElementAssessmentModel(
        name="protocolApplied", required=False, expected_value_assessment="compare_string")


class FHIRAssessmentModel(BaseModel):
    Patient = PatientAssessmentModel
    Encounter = EncounterAssessmentModel
    Organization = OrganizationAssessmentModel
    Location = LocationAssessmentModel
    Practitioner = PractitionerAssessmentModel
    Condition = ConditionAssessmentModel
    Procedure = ProcedureAssessmentModel
    Observation = ObservationAssessmentModel
    AllergyIntolerance = AllergyIntoleranceAssessmentModel


assessmentmodel_mapping = {
    "Patient": PatientAssessmentModel,
    "Encounter": EncounterAssessmentModel,
    "Organization": OrganizationAssessmentModel,
    "Location": LocationAssessmentModel,
    "Practitioner": PractitionerAssessmentModel,
    "Condition": ConditionAssessmentModel,
    "Procedure": ProcedureAssessmentModel,
    "Observation": ObservationAssessmentModel,
    "AllergyIntolerance": AllergyIntoleranceAssessmentModel,
    "Immunization": ImmunizationAssessmentModel
}
