# AI Emergency Call Intelligence System

A voice-in, text-out emergency call assistant. A caller speaks, the system
transcribes and extracts structured incident data one field at a time,
asks follow-up questions for whatever is still missing, and — once every
field is known — produces a formal incident report and a short set of
pre-arrival safety steps for the caller.

## Architecture

```
Streamlit UI (st.audio_input, mic recording)
       |
   Audio bytes (WAV) -> duration calculated
       |
OpenAI Whisper (whisper-1, audio.translations endpoint)
       |
   Transcript text
       |
GPT-4.1 mini structured extraction (OpenAI Responses API)
       |
State merge (new values fill "Unknown" slots, known values carry forward)
       |
Missing-field check -----> Follow-up question(s) shown to caller
       |                          |
       |                    (loop until all 6 fields are known)
       v
GPT-4.1 mini Incident Report (from full transcript)
       +
GPT-4.1 mini Pre-arrival Recommendation (from structured state)
       |
Streamlit display (sidebar transcript, JSON state, report, recommendations)
```

All stages are wrapped in `@traceable` (LangSmith) for tracing.

## Files and which stage they handle

| File | Stage |
|---|---|
| `input_fetch_convert.py` | Mic capture (`st.audio_input`) + Whisper speech-to-text |
| `extract_info.py` | GPT-4.1 mini structured field extraction |
| `check_info_followup.py` | State merge, missing-field detection, follow-up question generation |
| `generate_report_recommendation.py` | Incident report generation + pre-arrival safety recommendations |
| `app.py` | Streamlit app — session state, UI, wires every stage together |

## Fields extracted

`emergency_type`, `location`, `people_involved`, `injuries`, `hazards`, `severity`

Every field defaults to `"Unknown"` until the caller states it explicitly.
The extractor is instructed never to infer or guess a value — a hallucinated
field (a wrong location, an invented hazard) is a dispatch-safety issue, not
just an accuracy one. `hazards` distinguishes an explicit "no hazard" (`"None"`)
from "not mentioned yet" (`"Unknown"`), so the follow-up loop keeps asking
until the caller actually answers the hazard question rather than treating
silence as "safe."

## Setup

1. Create a virtual environment (recommended):
   ```
   python -m venv venv
   venv\Scripts\activate      (Windows)
   source venv/bin/activate   (Mac/Linux)
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Add a `.env` file with:
   ```
   OPENAI_API_KEY=your_key_here
   ```
   The key is read at import time via `python-dotenv` — unlike a session-entered
   key, this one needs to be in place before the app starts.

   For LangSmith tracing, also set the standard LangSmith environment
   variables (`LANGSMITH_API_KEY`, `LANGSMITH_TRACING=true`, and a project
   name) — tracing is optional; the app runs without it, just without traces.

4. Make sure `assets/emergency_bg.png` exists relative to `app.py` — the
   background styling loads this file directly and will error if it's missing.

5. Run the app:
   ```
   streamlit run app.py
   ```

## How it works, in plain words

1. **Speak** — the caller records a message through the browser mic button.
2. **Transcribe** — Whisper turns that recording into text. This is
   near-real-time and turn-based (record → submit → transcribe), not
   continuous streaming.
3. **Extract** — GPT-4.1 mini reads the latest turn only (not the whole
   call history, to keep cost from growing with every turn) and pulls out
   whichever of the 6 fields it can find, explicitly stated only.
4. **Merge & check** — new values fill in `"Unknown"` slots; anything the
   caller already gave stays put. Whatever is still `"Unknown"` after the
   merge becomes a follow-up question.
5. **Loop** — the caller answers, the cycle repeats, the gaps narrow.
6. **Report & recommend** — once all 6 fields are known, two things run in
   parallel: a four-section formal incident report generated from the full
   transcript (Incident Overview, Chronological Narrative, Critical
   Information Extracted, Dispatch and Response Summary), and a separate
   3–6 step pre-arrival safety recommendation generated from the structured
   field state — scene safety first, then confirming emergency services,
   then any hazard-specific first aid (burns, bleeding, gas leak, downed
   power line, unstable structure), then "follow the dispatcher's
   instructions."

## Design notes and known limitations

- **"Near-real-time," not real-time.** The Whisper API is batch, not
  streaming, so this is push-to-talk turn-taking rather than live
  transcription.
- **The recommendation step is a tightly-constrained LLM prompt, not a
  deterministic lookup table.** GPT-4.1 mini generates the pre-arrival
  steps directly, under a prompt that fixes the format, ordering, and which
  hazard-specific actions are allowed — rather than a rule table that
  looks up actions by emergency type outside the model entirely.
- **No inference, ever.** Every field — hazards included — is left
  `"Unknown"` unless the caller explicitly states it. This trades a few
  extra follow-up questions for not sending responders on a guess.
- **Live-mic capture is unreliable on Streamlit Community Cloud.** This is
  best run locally; a recorded demo video stands in for a live deployment
  demo.

## Cost notes

Both API calls in this project are paid OpenAI endpoints — `whisper-1`
for transcription and `gpt-4.1-mini` for extraction, report generation,
and recommendations. There's no free local component here (no local
embeddings or reranker), so cost scales with call volume and length.