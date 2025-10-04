import streamlit as st
import requests
from core.tts import speak
from datetime import datetime
import base64
import os
import io

# Custom CSS and JavaScript for modern chat UI and audio control
st.markdown("""
    <style>
    .chat-container {
        background-color: #f5f7fa;
        border-radius: 15px;
        padding: 20px;
        max-height: 500px;
        overflow-y: auto;
        border: 1px solid #e0e0e0;
        margin-bottom: 20px;
    }
    .user-message {
        background-color: #007bff;
        color: white;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin: 5px 10px 5px 50px;
        max-width: 70%;
        word-wrap: break-word;
        position: relative;
    }
    .ai-message {
        background-color: #e9ecef;
        color: #333;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin: 5px 50px 5px 10px;
        max-width: 70%;
        word-wrap: break-word;
        position: relative;
    }
    .timestamp {
        font-size: 0.7em;
        color: #666;
        margin-top: 2px;
        text-align: right;
    }
    .input-container {
        display: flex;
        align-items: center;
        gap: 10px;
        background-color: #fff;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
    }
    .stTextInput input {
        border: none !important;
        background-color: transparent !important;
        font-size: 1em;
    }
    .stButton button {
        background-color: #007bff;
        color: white;
        border-radius: 10px;
        padding: 8px 20px;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    .clear-button button {
        background-color: #dc3545;
        color: white;
        border-radius: 10px;
        padding: 8px 20px;
        border: none;
    }
    .clear-button button:hover {
        background-color: #b02a37;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: center;
    }
    audio {
        margin: 10px 0;
        width: 100%;
        max-width: 300px;
        border-radius: 5px;
    }
    .audio-container {
        margin: 5px 50px 5px 10px;
        max-width: 70%;
    }
    </style>
    <script id="audio-control-script">
    // Ensure script runs only once
    if (!window.audioControlInitialized) {
        window.audioControlInitialized = true;
        document.addEventListener('play', function(e) {
            console.log('Play event triggered for audio ID: ' + e.target.id);
            var allAudios = document.getElementsByTagName('audio');
            for (var i = 0; i < allAudios.length; i++) {
                if (allAudios[i] !== e.target) {
                    allAudios[i].pause();
                    allAudios[i].currentTime = 0;
                    console.log('Paused audio ID: ' + allAudios[i].id);
                }
            }
        }, true);
        // Function to play new audio and pause others
        window.playNewAudio = function(audioId) {
            var allAudios = document.getElementsByTagName('audio');
            for (var i = 0; i < allAudios.length; i++) {
                if (allAudios[i].id !== audioId) {
                    allAudios[i].pause();
                    allAudios[i].currentTime = 0;
                    console.log('Paused audio ID: ' + allAudios[i].id);
                }
            }
            var newAudio = document.getElementById(audioId);
            if (newAudio) {
                newAudio.play().catch(function(error) {
                    console.error('Autoplay failed: ' + error);
                });
            }
        };
    }
    </script>
""", unsafe_allow_html=True)

# Page title and favicon
st.set_page_config(page_title="ConvoFlow Chat", page_icon="💬", layout="centered")

# Title with gradient
st.markdown("<h1 style='text-align: center; background: linear-gradient(to right, #007bff, #00d4ff); -webkit-background-clip: text; color: transparent;'>ConvoFlow Chat</h1>", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container for messages
st.markdown('<div class="chat-container">', unsafe_allow_html=True)
for index, (sender, msg, timestamp, audio_base64) in enumerate(st.session_state.messages):
    if sender == "You":
        st.markdown(f'<div class="user-message">{msg}<div class="timestamp">{timestamp}</div></div>', unsafe_allow_html=True)
    elif sender == "AI":
        is_latest = (st.session_state.get("last_ai_message") == msg)
        audio_id = f"audio-{index}"  # Unique ID for each audio element
        st.markdown(f'<div class="ai-message">{msg}<div class="timestamp">{timestamp}</div></div>', unsafe_allow_html=True)
        # Display audio for all AI messages, no autoplay attribute - use script for latest
        if audio_base64:
            st.markdown(f'''
            <div class="audio-container">
                <audio id="{audio_id}" controls aria-label="AI response audio">
                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    Your browser does not support the audio element.
                </audio>
                <script>
                    if ({"true" if is_latest else "false"}) {{
                        window.playNewAudio("{audio_id}");
                    }}
                </script>
            </div>
            ''', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input container
with st.container():
    input_col, button_col, clear_col = st.columns([3, 1, 1])
    with input_col:
        user_input = st.text_input("You:", placeholder="Type your message...", key="user_input", label_visibility="collapsed")
    with button_col:
        send_button = st.button("Send", use_container_width=True)
    with clear_col:
        clear_button = st.button("Clear Chat", use_container_width=True, key="clear_button", help="Clear conversation history")

# Handle send button
if send_button and user_input:
    with st.spinner("Processing..."):
        try:
            # Send user input to FastAPI backend
            response = requests.post("http://127.0.0.1:8000/respond", data={"user_input": user_input})
            response.raise_for_status()
            data = response.json()

            ai_text = data.get("ai_response", "[Error]")
            current_time = datetime.now().strftime("%H:%M:%S")

            # Generate TTS and convert to base64
            audio_file = speak(ai_text)
            try:
                if isinstance(audio_file, bytes):
                    audio_base64 = base64.b64encode(audio_file).decode('utf-8')
                elif isinstance(audio_file, io.BytesIO):
                    audio_base64 = base64.b64encode(audio_file.getvalue()).decode('utf-8')
                else:
                    with open(audio_file, "rb") as audio_f:
                        audio_base64 = base64.b64encode(audio_f.read()).decode('utf-8')
            except Exception as e:
                st.markdown(f'<div class="error-message">TTS encoding error: {e}</div>', unsafe_allow_html=True)
                audio_base64 = None

            # Append messages (include audio_base64 for AI messages)
            st.session_state.messages.append(("You", user_input, current_time, None))
            st.session_state.messages.append(("AI", ai_text, current_time, audio_base64))
            st.session_state.last_ai_message = ai_text

            # Rerun to update UI and trigger autoplay via script
            st.rerun()

        except requests.RequestException as e:
            st.markdown(f'<div class="error-message">Error: Failed to connect to backend ({e}). Please ensure the server is running.</div>', unsafe_allow_html=True)
        except ValueError as e:
            st.markdown(f'<div class="error-message">Error: Invalid response from backend ({e}).</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="error-message">Error: {e}</div>', unsafe_allow_html=True)

# Handle clear button
if clear_button:
    st.session_state.messages = []
    if "last_ai_message" in st.session_state:
        del st.session_state.last_ai_message
    st.rerun()
