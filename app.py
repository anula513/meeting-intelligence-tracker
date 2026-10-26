from pathlib import Path

import streamlit as st
from answer import ask

EXAMPLES = [
    "Who owns the beta launch date?",
    "What did we decide about rolling back after the outage?",
    "Which API style will the Orbit integration use?",
    "What is the budget for the Mars mission?",
]


def use_example(text):
    st.session_state.question = text


st.title("Meeting Intelligence Tracker")
st.write(
    "Ask questions about 14 AI-generated sample meetings. "
    "Every answer shows a verified quote, or says it couldn't find one."
)

meeting_ids = sorted(p.stem for p in Path("sample_transcripts").glob("*.txt"))
choice = st.selectbox("Search in", ["All meetings"] + meeting_ids)
meeting_id = None if choice == "All meetings" else choice

if meeting_id:
    with st.expander("Read this transcript"):
        path = Path("sample_transcripts") / f"{meeting_id}.txt"
        st.text(path.read_text(encoding="utf-8"))

st.caption("Try an example:")
for example in EXAMPLES:
    st.button(example, on_click=use_example, args=(example,))

question = st.text_input("Ask a question about your meetings", key="question")

if st.button("Ask"):
    if not question.strip():
        st.warning("Type a question first.")
    else:
        with st.spinner("Searching your meetings..."):
            result = ask(question, meeting_id)

        status = result["status"]
        quote = result["source_quote"]
        meeting = f"{result['meeting_name']} · {result['meeting_date']}"

        if status == "verified":
            st.success(result["answer"])
            st.markdown(f"> {quote}")
            st.caption(meeting)
        elif status == "unverified":
            st.warning(
                f"{result['answer']}\n\n"
                "I couldn't verify the quote, so double-check this one."
            )
        else:
            st.info(result["answer"])