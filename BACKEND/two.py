import os
import io
import datetime
import re
from groq import Groq
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

# 1. Setup & Environment
load_dotenv()

# Initialize Clients
# Ensure your .env has GROQ_API_KEY and ELEVENLABS_API_KEY
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
eleven_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# Configuration Constants
STT_MODEL = "whisper-large-v3"       # Groq's super fast Whisper
EMOTION_MODEL = "llama-3.1-8b-instant" # Groq's fast inference model
TTS_MODEL = "eleven_turbo_v2_5"      # ElevenLabs Low Latency
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"    # Bella (Change if needed)

# ==========================================
#  LOGIC 1: DYNAMIC GREETING (LLM BASED)
# ==========================================

def get_llm_greeting():
    """Generates a dynamic greeting based on time of day."""
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        time_context = "morning"
    elif 12 <= hour < 17:
        time_context = "afternoon"
    else:
        time_context = "evening"

    prompt = (
        f"You are VedaBuddy, a warm Ayurvedic guide. "
        f"Generate a short, 1-sentence spoken greeting for the {time_context}. "
        f"Do NOT start with 'Namaste' every time. Be varied. "
        f"End by asking how you can help. Keep it under 15 words."
    )
    
    try:
        response = groq_client.chat.completions.create(
            model=EMOTION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9, # High creativity for greetings
            max_tokens=50
        )
        return response.choices[0].message.content.replace('"', '')
    except Exception as e:
        print(f"Greeting Error: {e}")
        return f"Good {time_context}, I am VedaBuddy. How may I heal you today?"

# ==========================================
#  LOGIC 2: SPEECH TO TEXT (STT) - EAR
# ==========================================

def transcribe_audio(audio_bytes):
    """
    Converts audio bytes (from browser) -> Text (via Groq Whisper).
    """
    if not audio_bytes:
        return None
    try:
        # Create a virtual file in memory with a filename
        # Groq requires a 'filename' attribute to know it's audio
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "input.wav" 

        transcription = groq_client.audio.transcriptions.create(
            file=audio_file, 
            model=STT_MODEL,
            response_format="text",
            language="en" # Force English for consistency, or remove for auto-detect
        )
        return transcription.strip()
    except Exception as e:
        print(f"STT Error: {e}")
        return None

# ==========================================
#  LOGIC 3: THE EMOTION WRAPPER (LEVEL 2 LLM)
# ==========================================

def make_answer_listenable(detailed_text: str):
    """
    LEVEL 2: Takes the Level 1 (RAG) long answer and converts it 
    into a short, human-like script for TTS.
    """
    system_prompt = (
        "You are the voice of VedaBuddy. You are speaking to a friend, not writing an essay.\n"
        "TASK: Summarize the provided Ayurvedic advice into 2-3 spoken sentences (max 40 words).\n"
        "TONE: Warm, motherly, soothing, and clear.\n"
        "RULES:\n"
        "1. Do NOT use bullet points or lists.\n"
        "2. Do NOT use standard greetings (Namaste) again if not needed.\n"
        "3. Focus on the 'Actionable Advice' (What should they do?).\n"
        "4. No formatting (bold/italic), just raw text for speech."
    )

    try:
        response = groq_client.chat.completions.create(
            model=EMOTION_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": detailed_text}
            ],
            temperature=0.7,
            max_tokens=150
        )
        script = response.choices[0].message.content
        
        # Cleanup: Remove any rogue brackets or asterisks
        clean_script = re.sub(r'\[.*?\]', '', script) # Remove [tags]
        clean_script = clean_script.replace('*', '')  # Remove *bold*
        return clean_script.strip()

    except Exception as e:
        print(f"Emotion Wrapper Error: {e}")
        # Fallback: Just return the first 2 sentences of the original text
        return ". ".join(detailed_text.split(".")[:2]) + "."

# ==========================================
#  LOGIC 4: TEXT TO SPEECH (TTS) - MOUTH
# ==========================================

def generate_voice(text: str):
    """Generates MP3 audio bytes using ElevenLabs Turbo."""
    if not text:
        return None
    try:
        # Returns a generator of bytes
        audio_generator = eleven_client.text_to_speech.convert(
            text=text,
            voice_id=VOICE_ID,
            model_id=TTS_MODEL,
            output_format="mp3_44100_128" # High quality MP3
        )
        
        # Consume the generator to get full bytes
        audio_bytes = b"".join(audio_generator)
        return audio_bytes

    except Exception as e:
        print(f"TTS Error: {e}")
        return None