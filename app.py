import streamlit as st
import input_fetch_convert
import extract_info
import check_info_followup
import generate_report_recommendation

st.set_page_config(page_title="AI Emergency Call")

st.title("🎤 AI Emergency Call")

if "transcripts" not in st.session_state:
    st.session_state.transcripts = []

if "extracted_info" not in st.session_state:
    st.session_state.extracted_info = {
        "emergency_type": "Unknown",
        "location": "Unknown",
        "people_involved": "Unknown",
        "injuries": "Unknown",
        "hazards": "Unknown",
        "severity": "Unknown"
    }

if "followup_questions" not in st.session_state:
    st.session_state.followup_questions = []

if "report" not in st.session_state:
    st.session_state.report = ""

if "recommendation" not in st.session_state:
    st.session_state.recommendation = ""

audio, duration = input_fetch_convert.record_audio()

if audio is not None and st.button("Submit Recording"):
    query = input_fetch_convert.speech_to_text(audio)

    if query: # keep call log in sidebar but then for phone user?
        st.session_state.transcripts.append({
            "text": query,
            "duration": duration
        })

        current_info = extract_info.extract_info(query)
        current_info, missing_fields = check_info_followup.check_missing_fields(
                        current_info,
                        st.session_state.extracted_info
                    )
        st.session_state.extracted_info = (current_info)

        st.session_state.followup_questions = check_info_followup.ask_follow(missing_fields)

        if not st.session_state.followup_questions:
            complete_transcript = " ".join(
                item["text"]
                for item in st.session_state.transcripts
            )

            st.session_state.report = (
                generate_report_recommendation.generate_report(
                    complete_transcript
                )
            )

            st.session_state.recommendation = (
                generate_report_recommendation.generate_recommendation(
                    st.session_state.extracted_info
                )
            )
        else:
            st.session_state.report = ""
            st.session_state.recommendation = ""
    else:
        st.error("No speech could be detected.")

for question in st.session_state.followup_questions:
    st.warning(question)

st.header("Transcript")

for item in st.session_state.transcripts:
    st.markdown(item["text"])
    st.caption(f"Audio duration: {item['duration']:.1f} seconds")

st.header("Extracted Info")
st.json(st.session_state.extracted_info)

if st.session_state.report:
    st.header("Incident Report")
    st.markdown(st.session_state.report)

if st.session_state.recommendation:
    st.header("Recommended Steps")
    st.markdown(st.session_state.recommendation)