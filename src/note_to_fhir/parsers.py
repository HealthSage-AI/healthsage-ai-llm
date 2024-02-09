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

import json
import re
import marko


def extract_from_code_block(markdown):
    parsed = marko.Parser().parse(markdown)
    code_block = [elem for elem in parsed.children if isinstance(
        elem, marko.block.FencedCode)]
    if len(code_block) > 0:
        raw_data = code_block[0].children[0].children
        return ''.join(raw_data)
    else:
        return markdown if '\n\n' not in markdown else markdown.split('\n\n')[1]


def parse_json_markdown(markdown_string: str) -> dict:
    json_str = extract_from_code_block(markdown_string)

    return json.loads(json_str)

def parse_json(s) -> str:
    
    # regular expression pattern to find text between ```json and ```
    pattern = re.compile(r'```json(.*?)```', re.DOTALL)
    
    # search the string for the pattern
    match = pattern.search(s)
    
    # check if a match was found
    if match:
        # extract the matched substring
        substring = match.group(1)
    
        # output the extracted substring
        return substring
    else:
        return "{}"
    
def parse_note_to_fhir(s) -> dict:
    """Parse FHIR JSON string from Note-to-Fhir output

    Args:
        s (_type_): _description_

    Returns:
        dict: _description_
    """
    fhir_json = s.split("```")[3][4:].strip(" \t\n\r")
    fhir = json.loads(fhir_json)
    return fhir
