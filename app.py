import streamlit as st
import input_fetch_convert

st.set_page_config(page_title="AI Emergency Call")

st.title("🎤 AI Emergency Call")

if "transcripts" not in st.session_state:
    st.session_state.transcripts = []

audio, duration = input_fetch_convert.record_audio()

if audio is not None and st.button("Submit Recording"):
    query = input_fetch_convert.speech_to_text(audio)

    if query: # future - add-on: keep call log in sidebar
        st.session_state.transcripts.append({
            "text": query,
            "duration": duration
        })
    else:
        st.error("No speech could be detected.")

st.header("Transcript")

for item in st.session_state.transcripts:
    st.markdown(item["text"])
    st.caption(f"Audio duration: {item['duration']:.1f} seconds")