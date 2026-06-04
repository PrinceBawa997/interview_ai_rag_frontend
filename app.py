import streamlit as st
import requests

# Page settings
st.set_page_config(
    page_title="Interview AI & RAG",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 Interview AI & RAG System")

# Sidebar
choice = st.sidebar.selectbox(
    "Select Module",
    ["Interview AI", "RAG AI"]
)

# =========================
# INTERVIEW AI
# =========================

if choice == "Interview AI":

    st.header("🎤 AI Interview Assistant")

    topic = st.text_input(
        "Enter Topic",
        placeholder="Python, Java, DBMS"
    )

    if st.button("Start Interview"):

        response = requests.post(
            "http://127.0.0.1:8000/topic",
            json={"topic": topic}
        )

        question = response.json()["topic"]

        st.session_state["question"] = question

    if "question" in st.session_state:

        st.subheader("Question")

        st.info(st.session_state["question"])

        answer = st.text_area(
            "Your Answer"
        )

        if st.button("Submit Answer"):

            response = requests.post(
                "http://127.0.0.1:8000/answer",
                json={"Answer": answer}
            )

            result = response.json()["Answer"]

            st.subheader("Interview Feedback")

            st.success(result)

# =========================
# RAG AI
# =========================

elif choice == "RAG AI":

    st.header("📚 PDF Question Answering")

    pdf = st.file_uploader(
        "Upload PDF",
        type=["pdf"]
    )

    if pdf is not None:

        files = {
            "file": (
                pdf.name,
                pdf.getvalue(),
                "application/pdf"
            )
        }

        response = requests.post(
            "http://127.0.0.1:8000/pdf",
            files=files
        )

        st.success("PDF Uploaded Successfully")

    question = st.text_input(
        "Ask Question From PDF"
    )
    if st.button("Ask AI"):

        try:

            response = requests.post(
                "http://127.0.0.1:8000/ask",
                json={"question": question}
            )

            if response.status_code == 200:

                data = response.json()

                if "answer" in data:

                    st.subheader("Answer")
                    st.write(data["answer"])

                elif "error" in data:

                    st.error(data["error"])

                else:

                    st.error("Unexpected response")
                    st.write(data)

            else:

                st.error(f"API Error: {response.status_code}")
                st.text(response.text)

        except Exception as e:

            st.error(f"Error: {e}")