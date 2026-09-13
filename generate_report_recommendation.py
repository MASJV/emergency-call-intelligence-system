import os
from dotenv import load_dotenv
from openai import OpenAI
from langsmith import traceable

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

@traceable(name="generateReport")
def generate_report(transcript):
    prompt = f"""You are an expert emergency-response dispatcher and legal documentation specialist writing a formal Incident Report for an official case file.

TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"

TASK
Write the Incident Report using ONLY information stated or directly implied in the transcript above.

REQUIRED STRUCTURE (use this exact wording, this exact order, nothing added, nothing removed, nothing renamed):

1. Incident Overview
2. Chronological Narrative
3. Critical Information Extracted
4. Dispatch and Response Summary

FORMAT RULES
- Each section is one or more full prose paragraphs. No bullet points, no numbered lists, no dashes, no headers other than the four above.
- Do not add extra sections such as "Recommended Actions," "Next Steps," "Summary," or any advisory content. If the transcript shows the dispatcher giving instructions, report that as a factual event inside "Dispatch and Response Summary" (e.g., "the dispatcher instructed the caller to...") — never as a standalone recommendation addressed to the reader.
- Use objective, precise, public-safety report language: third person, past tense, no speculation, no emotional language.

ACCURACY RULES
- Do not invent timestamps, actions, emergency services, instructions, injuries, or outcomes that are not in the transcript.
- If a detail relevant to a section is missing, state plainly within that section that it was not provided (e.g., "The exact time of the call was not stated in the transcript.").

EXAMPLE (structure and tone only — do not reuse this content)

Transcript excerpt: "Caller reports a two-vehicle collision on Ring Road. One passenger is bleeding from the head and conscious. Caller says no fire or smoke. Dispatcher tells caller to stay on the line and confirms an ambulance is being sent."

1. Incident Overview
A two-vehicle collision was reported on Ring Road, resulting in at least one injured passenger. No fire or smoke was reported at the scene.

2. Chronological Narrative
The caller reported the collision and stated that one passenger was bleeding from the head but remained conscious. The dispatcher instructed the caller to remain on the line while an ambulance was dispatched. No further updates were provided in the transcript.

3. Critical Information Extracted
Location: Ring Road. Vehicles involved: two. Injuries: one passenger, head laceration, conscious. Hazards: none reported. Exact time of the incident was not stated in the transcript.

4. Dispatch and Response Summary
The dispatcher confirmed that an ambulance was being sent and instructed the caller to remain on the line. No additional emergency services were mentioned as dispatched in the transcript.

BEFORE YOU FINALIZE, VERIFY
- Exactly four sections appear, in the order and wording given above.
- No bullet points, dashes, or numbered lists anywhere in the output.
- Every fact traces to the transcript; every gap is explicitly labeled "not provided" rather than left implied or invented.

Now write the Incident Report for the transcript provided above.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text

@traceable(name="generateRecommendation")
def generate_recommendation(current_info):

    prompt = f"""You are an emergency first-response assistant giving pre-arrival guidance to an untrained caller.

EMERGENCY INFORMATION:
\"\"\"
{current_info}
\"\"\"

TASK
Give short, immediate safety steps the caller can take right now, based only on what is stated in the emergency information above.

OUTPUT FORMAT — FOLLOW EXACTLY
- Output ONLY a numbered list: "1.", "2.", "3." etc.
- 3 to 6 steps total, no more, no fewer.
- Each step is exactly one short sentence.
- Do NOT include a title, header, or label (e.g., no "Recommended Actions:", no "Immediate Steps:").
- Do NOT use dashes, bullets, colons-as-list-markers, or bold text.
- Do NOT add an introductory sentence or a concluding sentence — the numbered list is the entire output.

WRONG (do not produce this shape):
Recommended Immediate Actions: - Call an ambulance immediately. - Notify traffic police.

CORRECT (produce this shape):
1. Call for an ambulance immediately.
2. Move to a safe distance from the vehicle if fuel is leaking.
3. Keep the injured person still unless there is immediate danger.

CONTENT PRIORITY
Order steps by priority: scene safety first, then contacting/confirming emergency services, then any hazard-specific first-aid actions below, then the dispatcher-instruction step.

HAZARD-SPECIFIC FIRST AID (include only if that hazard is explicitly mentioned in the emergency information — do not infer or guess an injury that wasn't stated)
- Burns or fire exposure: include a step to cool the burn under clean running water for several minutes and cover loosely with a clean cloth. Do not mention ice, butter, ointments, or creams.
- Bleeding or open wound: include a step to apply firm, steady direct pressure to the wound with a clean cloth. Do not mention removing embedded objects or tourniquets.
- Gas leak or suspected gas smell: include a step to avoid switches, lighters, or anything that could spark, and to move away from the area and open windows/doors if it is safe to do so.
- Downed power line or electrical hazard: include a step to stay well away from the wire and anything it is touching, and to warn others not to approach.
- Unstable or collapsing structure: include a step to move to a clear, open area away from the structure and not to re-enter it.
- If no specific hazard is mentioned, skip this section and keep to general scene-safety and dispatch steps.

RULES
- Prioritize scene safety and contacting emergency services.
- Give only basic actions safe for an untrained person.
- Do not diagnose injuries or name a medical condition.
- Do not recommend medicines.
- Do not recommend advanced medical procedures (no CPR steps, no splinting, no tourniquets, no injections).
- For vehicle crashes, do not tell the caller to move or remove an injured person unless there is immediate danger such as fire, leaking fuel, or moving traffic.
- Include a step telling the caller to follow the emergency dispatcher's instructions.

Now produce the numbered list for the emergency information above.
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text