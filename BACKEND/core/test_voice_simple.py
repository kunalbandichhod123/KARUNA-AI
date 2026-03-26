from elevenlabs import ElevenLabs
import os

# --- PASTE YOUR KEY HERE DIRECTLY ---
# 🛡️ CRITICAL FIX: FORCE THE WORKING KEY
# We bypass .env to ensure the "Missing Permissions" error never happens again.
MY_ELEVEN_KEY = "sk_69e3577247251f733ab2b9c1bdcafb48c73554ced17c77ad"
eleven_client = ElevenLabs(api_key=MY_ELEVEN_KEY) # I kept your key here for this test

client = ElevenLabs(api_key=MY_KEY)

print("Attempting to generate voice...")

try:
    # FIX: Changed model_id to the correct one
    audio = client.text_to_speech.convert(
        text="This is a test of your API key.",
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Rachel
        model_id="eleven_turbo_v2_5"      # <--- THIS WAS THE PROBLEM
    )
    
    # Consume the generator
    audio_bytes = b"".join(audio)
    
    print("\nSUCCESS! The key works.")
    print(f"Received {len(audio_bytes)} bytes of audio.")

except Exception as e:
    print("\nFAILED. The Error is:")
    print(e)