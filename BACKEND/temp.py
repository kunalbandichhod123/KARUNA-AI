import os
import base64
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- IMPORTS ---
import voice_engine as ve

# TRY to import your RAG engine. 
# If this fails, the code will crash, so ensure 'query_engine.py' exists.
try:
    from query_engine import generate_answer
except ImportError:
    print("WARNING: 'query_engine.py' not found. Using dummy RAG response.")
    def generate_answer(q, session_id=None):
        return "This is a dummy response because query_engine is missing. Ayurveda recommends Ashwagandha."

app = FastAPI(title="VedaBuddy API")

# ==========================================
#  CORS SETUP (Allow Frontend Access)
# ==========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Models ---
class ChatRequest(BaseModel):
    question: str
    session_id: str = "web_user_1"

# ==========================================
#  ENDPOINT 1: INITIAL GREETING (Voice Mode Start)
# ==========================================
@app.get("/greeting")
async def get_greeting():
    """
    Triggered when user clicks the Mic icon.
    Returns: { text: "Good Morning...", audio: "base64..." }
    """
    # 1. Generate Text
    text = ve.get_llm_greeting()
    
    # 2. Generate Audio
    audio_bytes = ve.generate_voice(text)
    
    if not audio_bytes:
        raise HTTPException(status_code=500, detail="Failed to generate greeting audio")
    
    # 3. Encode to Base64 for easy Frontend playback
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    
    return {
        "text": text,
        "audio": f"data:audio/mp3;base64,{audio_b64}"
    }

# ==========================================
#  ENDPOINT 2: VOICE PROCESSOR (The 2-Level Loop)
# ==========================================
@app.post("/voice-process")
async def voice_process(file: UploadFile = File(...)):
    """
    The Core Loop:
    Audio In -> Whisper -> Text -> RAG (Level 1) -> Emotion (Level 2) -> TTS -> Audio Out
    """
    try:
        # Step 0: Read Audio File
        audio_bytes = await file.read()
        
        # Step 1: Transcribe (STT) - "The Ear"
        user_query = ve.transcribe_audio(audio_bytes)
        if not user_query:
            return {"error": "I couldn't hear anything clearly."}
        print(f"User Asked: {user_query}")

        # Step 2: Level 1 LLM (RAG / The Brain)
        # This generates the Long, Accurate Answer for the Chat History
        full_rag_answer = generate_answer(user_query, session_id="voice_user")
        print("RAG Answer Generated.")

        # Step 3: Level 2 LLM (The Performer)
        # This converts the Long Answer into a Short Script for Speech
        voice_script = ve.make_answer_listenable(full_rag_answer)
        print(f"Voice Script: {voice_script}")

        # Step 4: TTS (ElevenLabs) - "The Mouth"
        audio_out_bytes = ve.generate_voice(voice_script)
        
        # Encode Response
        audio_b64 = None
        if audio_out_bytes:
            audio_b64 = base64.b64encode(audio_out_bytes).decode("utf-8")

        return {
            "transcript": user_query,      # Show this under the Sphere
            "chat_answer": full_rag_answer, # Append this to the Chat UI History
            "voice_script": voice_script,   # (Optional) Debugging
            "audio": f"data:audio/mp3;base64,{audio_b64}" if audio_b64 else None
        }

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
#  ENDPOINT 3: STANDARD CHAT (Text Fallback)
# ==========================================
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Standard RAG chat for the text box."""
    answer = generate_answer(request.question, session_id=request.session_id)
    return {"answer": answer}

# Run with: python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)