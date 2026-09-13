import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from langsmith import traceable

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@traceable(name="extractInfo")
def extract_info(current_query):

    prompt = f"""
# Role
You are an expert real-time emergency dispatch data extractor.
Analyze the latest emergency-call query and extract critical incident information.

# Instructions
- Extract information only from explicit statements or very high-confidence inferences.
- If a field is not mentioned, unclear, incomplete, or possibly misheard, set it to "Unknown".
- For location, accept only a clear and plausible address, area, landmark, street, city, or proper place name.
- Do not treat random words, broken phrases, or unclear sounds as locations.
- If the caller clearly corrects a location, extract the corrected location.
- Example: "It is not Vastrapur, it is Navrangpura" means location is "Navrangpura".
- If the correction is unclear or the new location does not sound like a legitimate place name, return "Unknown" for location.
- Never guess or autocorrect an uncertain location.
- Return exactly one valid JSON object.
- Do not return markdown, code fences, explanations, or extra text.
- severity can be accessed based on keywords like "immediately" means medium-high while other parameters like people involved are unknown.

# Fields to Extract
1. emergency_type
2. location
3. people_involved
4. injuries
5. hazards: an ongoing environmental or safety danger at the scene (e.g. fire, smoke, gas leak, downed power line, unstable/collapsing structure, chemical spill, armed person).
   - Extract only if the caller explicitly states it. Never infer a hazard from the emergency_type alone — a "car accident" is not automatically a fire or fuel-leak hazard unless the caller says so.
   - If the caller explicitly says there is no hazard, set this to "None".
   - If hazards are simply not mentioned either way, set this to "Unknown".
6. severity: strictly "Low", "Medium", "High", "Critical", or "Unknown"

# Required JSON Format
{{
    "emergency_type": "value or Unknown",
    "location": "value or Unknown",
    "people_involved": "value or Unknown",
    "injuries": "value or Unknown",
    "hazards": "value, None, or Unknown",
    "severity": "Low, Medium, High, Critical or Unknown"
}}

Query:
{current_query}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return json.loads(response.output_text)