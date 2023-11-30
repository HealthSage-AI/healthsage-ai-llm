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


class FhirClient:
    def __init__(self, session):
        self.session = session
        self.token = get_token(session)

    def create_resource(self, resource):
        resource_type = resource["resourceType"]
        resp = self.session.post(f'/fhir/R4/{resource_type}', json=resource,
                                 headers={"Authorization": f"Bearer {self.token}",
                                          "Content-Type": "application/fhir+json"})
        resp.raise_for_status()
        return resp.json()

    def validate(self, fhir_resources):
        return [self.validate_resource(response) for response in fhir_resources]

    def validate_resource(self, resource):
        resource_type = resource["resourceType"]
        resp = self.session.post(f'/fhir/R4/{resource_type}/$validate', json=resource,
                                 headers={"Authorization": f"Bearer {self.token}",
                                          "Content-Type": "application/fhir+json"})
        return resp.json()


def get_token(session):
    client_id = os.getenv('MEDPLUM_CLIENT_ID', 'MEDPLUM_CLIENT_ID not defined')
    client_secret = os.getenv('MEDPLUM_CLIENT_SECRET', 'MEDPLUM_CLIENT_SECRET not set')
    resp = session.post('/oauth2/token',
                        data={'grant_type': 'client_credentials',
                              'client_id': client_id, 'client_secret': client_secret})
    resp.raise_for_status()
    return resp.json()['access_token']
