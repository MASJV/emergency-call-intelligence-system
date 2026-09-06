import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_report(transcript):
    prompt = f"""
Act as an expert emergency response dispatcher and legal documentation specialist.
Analyze the provided emergency call transcript and write a formal Incident Report.

Use objective, precise, and professional public-safety language.

Structure the report under these headings:

1. Incident Overview
2. Chronological Narrative
3. Critical Information Extracted
4. Dispatch and Response Summary

Rules:
- Use only information available in the transcript.
- Do not invent timestamps, actions, emergency services, instructions, or outcomes.
- If information is unavailable, clearly state that it was not provided.
- Write full paragraphs without bullet points.

Emergency call transcript:
{transcript}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text

def generate_recommendation(current_info):

    prompt = f"""
You are an emergency first-response assistant.

Based on the emergency information below, provide short and immediate
safety steps for the caller.

Rules:
- Return only 3 to 6 short numbered steps.
- Each step must be one short sentence.
- Prioritize scene safety and contacting emergency services.
- Give only basic actions safe for an untrained person.
- Do not diagnose injuries.
- Do not recommend medicines.
- Do not recommend advanced medical procedures.
- For vehicle crashes, do not tell the caller to move or remove an
  injured person unless there is immediate danger such as fire,
  leaking fuel, or moving traffic.
- Tell the caller to follow instructions from the emergency dispatcher.
- Do not return introductory or concluding paragraphs.

Emergency information:
{current_info}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text