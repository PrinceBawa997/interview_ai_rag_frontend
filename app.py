import streamlit as st
import requests

# =========================
# CONFIG
# =========================
API_URL = "https://interview-ai-rag-production.up.railway.app"

st.set_page_config(
    page_title="Interview AI & RAG",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Interview AI & RAG System")

# =========================
# SIDEBAR
# =========================
choice = st.sidebar.selectbox(
    "Select Module",
    ["Interview AI", "RAG AI"]
)

# =========================
# INTERVIEW AI
# =========================
if choice == "Interview AI":

    st.header("🎤 AI Interview Assistant")

    topic = st.text_input("Enter Topic", placeholder="Python, Java, DBMS")

    if st.button("Start Interview"):

        try:
            response = requests.post(
                f"{API_URL}/topic",
                json={"topic": topic}
            )

            if response.status_code == 200:
                data = response.json()
                st.session_state["question"] = data.get("topic", "No question returned")
            else:
                st.error(response.text)

        except Exception as e:
            st.error(f"Connection Error: {e}")

    if "question" in st.session_state:

        st.subheader("Question")
        st.info(st.session_state["question"])

        answer = st.text_area("Your Answer")

        if st.button("Submit Answer"):

            try:
                response = requests.post(
                    f"{API_URL}/answer",
                    json={"Answer": answer}
                )

                if response.status_code == 200:
                    data = response.json()
                    st.subheader("Interview Feedback")
                    st.success(data.get("Answer", "No feedback returned"))
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Connection Error: {e}")

# =========================
# RAG AI
# =========================
elif choice == "RAG AI":

    st.header("📄 PDF Question Answering")

    pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf is not None:

        if st.button("Upload PDF"):

            try:
                files = {
                    "file": (pdf.name, pdf.getvalue(), "application/pdf")
                }

                response = requests.post(
                    f"{API_URL}/pdf",
                    files=files
                )

                if response.status_code == 200:
                    st.success("PDF Uploaded Successfully")
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Connection Error: {e}")

    question = st.text_input("Ask Question From PDF")

    if st.button("Ask AI"):

        try:
            response = requests.post(
                f"{API_URL}/ask",
                json={"question": question}
            )

            if response.status_code == 200:
                data = response.json()

                if "answer" in data:
                    st.subheader("Answer")
                    st.write(data["answer"])
                else:
                    st.error(data.get("error", "Unexpected response"))

            else:
                st.error(response.text)

        except Exception as e:
            st.error(f"Connection Error: {e}")