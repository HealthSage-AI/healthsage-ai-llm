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

count_resource_template = """Preparation step for generating HL7 FHIR R4 Resource {1}. \n 
Instructions: \n 
1. We are only interested in {1} related information. Filter out what information in the clinical note is relevant for a HL7 FHIR resource of type {1}.\n
2. There could be multiple elements needed. Determine which {1} elements need to be made to cover the available info. There could be zero, one or multiple resources needed.
3. Return a json string that labels the seperate elements in a single word, so they can be identified later on. \n
\n
Here is the clinical note:
\nBEGIN NOTE\n{0}. \nEND NOTE \n
\n
Here is an example output:
{{1: somelabel
2: otherlabel
3: final label}}
Return an empty dict if there is no information about {1} in the note.
"""
