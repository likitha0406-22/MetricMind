import streamlit as st
import requests

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="MetricMind",
    page_icon="📊",
    layout="wide"
)

# -----------------------------
# Title
# -----------------------------
st.title("📊 MetricMind")
st.subheader("AI-Powered Data Analytics Assistant")

st.write(
    "Ask questions about your dataset and get data-driven insights "
    "using MetricMind AI."
)

# -----------------------------
# FastAPI Backend
# -----------------------------
API_URL = "http://127.0.0.1:8000/chat"

# -----------------------------
# Chat History
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# Chat Input
# -----------------------------
question = st.chat_input("Ask MetricMind about your data...")

if question:

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    # Send question to FastAPI
    try:
        response = requests.post(
            API_URL,
            json={"message": question}
        )

        if response.status_code == 200:

            data = response.json()
            answer = data.get("reply", "No response received.")

            # Show AI response
            with st.chat_message("assistant"):
                st.markdown(answer)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })

        else:
            st.error(
                f"Backend error: {response.status_code}\n\n"
                f"{response.text}"
            )

    except requests.exceptions.ConnectionError:
        st.error(
            "❌ Could not connect to the FastAPI backend.\n\n"
            "Make sure your FastAPI server is running on "
            "http://127.0.0.1:8000"
        )

    except Exception as e:
        st.error(f"Error: {e}")