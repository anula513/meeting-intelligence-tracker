import streamlit as st
from answer import ask

st.title("Meeting Intelligence Tracker")

question = st.text_input("Ask a question about your meetings")

if st.button("Ask"):
    if not question.strip():
        st.warning("Type a question first.")
    else:
        with st.spinner("Searching your meetings..."):
            result = ask(question)

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