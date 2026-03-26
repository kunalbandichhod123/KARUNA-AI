from elevenlabs import ElevenLabs

# HARDCODE THE KEY HERE JUST FOR THIS TEST
# Do not use os.getenv. Paste the string directly to be 100% sure.
KEY = "sk_69e3577247251f733ab2b9c1bdcafb48c73554ced17c77ad"

client = ElevenLabs(api_key=KEY)

print("Attempting to speak...")

try:
    audio = client.text_to_speech.convert(
        text="Hello! The new API key is working perfectly.",
        voice_id="EXAVITQu4vr4xnSDxMaL", # Bella
        model_id="eleven_turbo_v2_5"
    )
    
    # Save to verify
    with open("test_output.mp3", "wb") as f:
        f.write(b"".join(audio))
        
    print("SUCCESS! 'test_output.mp3' was created. The Key is valid.")

except Exception as e:
    print("\nFAILED!")
    print(f"Error Message: {e}")