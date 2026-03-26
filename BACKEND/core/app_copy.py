import streamlit as st
from query_engine import generate_answer

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="VedaBuddy - Ayurveda Assistant",
    page_icon="🌿",
    layout="wide" 
)

# --- CUSTOM STYLING (Untouched) ---
st.markdown("""
    <style>
    .main {
        background-color: #fdfcf0; 
    }
    .stChatMessage {
        border-radius: 15px;
        padding: 10px;
        margin-bottom: 10px;
    }
    .st-emotion-cache-1c7n2ka { 
        background-color: #e8f5e9; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR (Untouched) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2913/2913520.png", width=100)
    st.title("VedaBuddy Settings")
    st.info("Your AI-powered guide to ancient Ayurvedic wisdom.")
    
    st.divider()
    
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
        
    st.write("---")
    st.caption("Disclaimer: This tool provides information based on Vedic texts and is not a substitute for professional medical advice.")

# --- MAIN INTERFACE ---
st.title("🌿 VedaBuddy")
st.markdown("##### *Your Personal Ayurvedic Caretaker*")

# Initialize chat history
if "messages" not in st.session_state:
    # Starting with a proactive greeting as per the "Vaidya" persona
    st.session_state.messages = [
        {"role": "assistant", "content": "Namaste! I am Vaidya. How can I help you balance your Doshas or improve your wellbeing today?"}
    ]

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC WITH MID-RANGE MEMORY ---
if prompt := st.chat_input("Ask about Doshas, Diet, or Herbs..."):
    # 1. Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 2. Add user message to history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. Generate response with History
    with st.chat_message("assistant"):
        with st.spinner("Consulting Vedic texts..."):
            # MEMORY LOGIC: We pass the last 20 messages so Vaidya stays focused 
            # and remembers previous details about the user's health.
            history_context = st.session_state.messages[-20:]
            
            # Note: Ensure your generate_answer function in query_engine.py 
            # is updated to accept 'history' as an argument.
            # We now use session_id instead of passing the history string manually
            response = generate_answer(prompt, session_id="streamlit_user")
            st.markdown(response)
    
    # 4. Add assistant response to history
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Optional: Keep the session state itself from growing too large (Memory Management)
    if len(st.session_state.messages) > 30:
        # Keep the initial greeting + the last 20 messages
        st.session_state.messages = [st.session_state.messages[0]] + st.session_state.messages[-20:]