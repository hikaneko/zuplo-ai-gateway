import streamlit as st
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Gemini Chat (Zuplo)",
    page_icon="💬",
    layout="centered"
)

# Title
st.title("💬 Gemini Chat via Zuplo")

# Zuplo AI Gateway endpoint
ZUPLO_ENDPOINT = "https://<YOUR Endpoint>.zuplo.app/v1/chat/completions"

# Sidebar for API key input
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Zuplo API Key", type="password")

    if api_key:
        st.success("API key configured")
    else:
        st.warning("Please enter your API key")

    st.markdown("---")
    st.markdown("### Model Settings")
    model_name = st.selectbox(
        "Model",
        ["gemini-2.5-flash-lite", "gemini-2.5-flash"],
        index=0
    )

    st.markdown("---")
    st.markdown("### How to Use")
    st.markdown("1. Enter your Zuplo API key in the field above")
    st.markdown("2. Type your message in the chat input below")
    st.markdown("3. Press Enter to send")

# Warning if API key is not set
if not api_key:
    st.info("👈 Please enter your Zuplo API key in the sidebar")
    st.stop()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("Enter your message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()

        try:
            # Call Gemini API via Zuplo AI Gateway
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            # Create request in OpenAI-compatible format
            payload = {
                "model": model_name,
                "messages": [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in st.session_state.messages
                ]
            }

            response = requests.post(
                ZUPLO_ENDPOINT,
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                full_response = result["choices"][0]["message"]["content"]

                # Display response
                message_placeholder.markdown(full_response)

                # Add assistant message to history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response
                })
            else:
                error_message = f"Error (Status Code: {response.status_code}): {response.text}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })

        except requests.exceptions.Timeout:
            error_message = "Request timed out. Please try again."
            message_placeholder.error(error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            message_placeholder.error(error_message)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_message
            })

# Clear chat history button
if st.session_state.messages:
    if st.sidebar.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
