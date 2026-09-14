# 🚨 AI Emergency Call Intelligence System

A voice-in, text-out emergency call assistant. A caller speaks, the system
transcribes and extracts structured incident data one field at a time,
asks follow-up questions for whatever is still missing, and — once every
field is known — produces a formal incident report and a short set of
pre-arrival safety steps for the caller.

## 🏗️ Architecture

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

## 📁 Files and which stage they handle

| File | Stage |
|---|---|
| `input_fetch_convert.py` | Mic capture (`st.audio_input`) + Whisper speech-to-text |
| `extract_info.py` | GPT-4.1 mini structured field extraction |
| `check_info_followup.py` | State merge, missing-field detection, follow-up question generation |
| `generate_report_recommendation.py` | Incident report generation + pre-arrival safety recommendations |
| `app.py` | Streamlit app — session state, UI, wires every stage together |

## 📋 Fields extracted

`emergency_type`, `location`, `people_involved`, `injuries`, `hazards`, `severity`

Every field defaults to `"Unknown"` until the caller states it explicitly.
The extractor is instructed never to infer or guess a value — a hallucinated
field (a wrong location, an invented hazard) is a dispatch-safety issue, not
just an accuracy one. `hazards` distinguishes an explicit "no hazard" (`"None"`)
from "not mentioned yet" (`"Unknown"`), so the follow-up loop keeps asking
until the caller actually answers the hazard question rather than treating
silence as "safe."

## ⚙️ Setup

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

## 🗣️ How it works, in plain words

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

## ✨ Enhancements

Beyond the base capstone requirements:

- [x] Tracing and observability — every stage wrapped in LangSmith `@traceable`
- [x] Audio (speech-to-text) evaluation — Word Error Rate scoring via jiwer

## 📊 Evaluation

### 🎙️ Audio / speech-to-text (jiwer, WER)

`evaluation/evaluate_audio.py` runs a fixed set of 10 recorded test clips
against the same `speech_to_text()` function the app uses in production —
not a copy or reimplementation, the actual function. Each clip's Whisper
output is scored against a hand-typed reference transcript using Word
Error Rate, with a normalization pass (lowercase, punctuation stripped)
so formatting differences don't count as errors.

`evaluation/audio_test_cases.json` holds the clip-to-reference mapping.
The clips themselves aren't committed (`evaluation/test_clips/` is
gitignored, since they're personal voice recordings) — the reference
JSON and the sample output below are kept as the record of what was
said and how the run went.

Sample output from a run:

```
evaluation/test_clips/clip1.m4a: WER = 0.087
  reference : There's been a car accident on SG Highway near the Iskcon crossroads, two cars collided and one person is bleeding from the head.
  hypothesis: There has been a car accident on SG highway near the ISKCON crossroads, two cars collided and one person is bleeding from the head.

evaluation/test_clips/clip2.m4a: WER = 0.125
  reference : There's a fire in the kitchen of my apartment on the third floor, the smoke is spreading fast and I need help right now.
  hypothesis: There is a fire in the kitchen of my apartment on the 3rd floor. The smoke is spreading fast and I need help right now.

evaluation/test_clips/clip3.m4a: WER = 0.267
  reference : My neighbor just collapsed on the stairs and he's not responding, I think he's unconscious.
  hypothesis: My neighbor just collapsed on the stairs and he is not responding. I think he is unconscious.

evaluation/test_clips/clip4.m4a: WER = 0.0
  reference : There's a gas leak in our building, I can smell it strongly near the parking area, please send someone immediately.
  hypothesis: There's a gas leak in our building. I can smell it strongly near the parking area. Please send someone immediately.

evaluation/test_clips/clip5.m4a: WER = 0.0
  reference : A motorcycle skidded and fell near Vastrapur lake, the rider seems conscious but his leg looks injured.
  hypothesis: A motorcycle skidded and fell near Vastrapur lake. The rider seems conscious but his leg looks injured.

evaluation/test_clips/clip6.m4a: WER = 0.0
  reference : There's a small crowd gathered after a fight broke out near the market, no one seems seriously hurt but it's getting loud.
  hypothesis: There's a small crowd gathered after a fight broke out near the market. No one seems seriously hurt, but it's getting loud.

evaluation/test_clips/clip7.m4a: WER = 0.05
  reference : A power line fell down after the storm near my house on Navrangpura main road, nobody has touched it yet.
  hypothesis: A power line fell down after the storm near my house on Novrankura Main Road, nobody has touched it yet.

evaluation/test_clips/clip8.m4a: WER = 0.0
  reference : There's been a robbery at the shop next to my house, the owner is shaken but not hurt.
  hypothesis: There's been a robbery at the shop next to my house. The owner is shaken but not hurt.

evaluation/test_clips/clip9.m4a: WER = 0.0
  reference : Part of the ceiling in the old building near Law Garden has collapsed, a few people are trapped inside.
  hypothesis: Part of the ceiling in the old building near law garden has collapsed. A few people are trapped inside.

evaluation/test_clips/clip10.m4a: WER = 0.133
  reference : My friend is having chest pain and difficulty breathing, we are at home in Bopal.
  hypothesis: My friend is having chest pain and difficulty in breathing. We are at home in Bhopal.

Overall WER across 10 clips: 0.062
```

Most of the non-zero clips trace back to phrasing, not mishearing —
Whisper writing "there has been" instead of "there's", or "3rd" instead
of "third." The two errors that are genuine mishearings — clip 7
("Navrangpura" → "Novrankura") and clip 10 ("Bopal" → "Bhopal") — both
land on the `location` field specifically, which is the more relevant
finding than the pooled 0.062 number on its own: local place names are
a real weak point for Whisper here, independent of how well the
downstream extraction prompt is written.

## 💰 Cost notes

Both API calls in this project are paid OpenAI endpoints — `whisper-1`
for transcription and `gpt-4.1-mini` for extraction, report generation,
and recommendations.