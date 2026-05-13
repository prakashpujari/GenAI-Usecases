import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

speech_file_path = "speech.wav" 
model = "playai-tts"
voice = "Fritz-PlayAI"
text = "I love exploring ai in depth to build gen ai and agentic ai applications!"
import os
import sys
import subprocess

speech_file_path = "speech.wav"
text = "I love exploring ai in depth to build gen ai and agentic ai applications!"

def try_use_groq(text, out_path):
    try:
        from groq import Groq
    except Exception:
        return False

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return False

    try:
        client = Groq(api_key=api_key)
        model = "playai-tts"
        voice = "Fritz-PlayAI"
        response_format = "wav"
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            response_format=response_format,
        )
        response.write_to_file(out_path)
        return True
    except Exception:
        return False

def ensure_comtypes():
    try:
        import comtypes  # type: ignore
        return True
    except Exception:
        # attempt to install comtypes into the current Python environment
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "comtypes"])
            import comtypes  # type: ignore
            return True
        except Exception:
            return False

def synthesize_with_sapi(text, out_path):
    # Windows SAPI via comtypes — produces a WAV file
    if not ensure_comtypes():
        raise RuntimeError("comtypes is required for the local fallback. Install it and retry.")

    import comtypes.client  # type: ignore

    speaker = comtypes.client.CreateObject("SAPI.SpVoice")
    stream = comtypes.client.CreateObject("SAPI.SpFileStream")
    # Use numeric constant for SSFMCreateForWrite (3) to avoid requiring generated typelib
    stream.Open(out_path, 3)
    speaker.AudioOutputStream = stream
    speaker.Speak(text)
    stream.Close()


if __name__ == "__main__":
    # Try Groq first (requires GROQ_API_KEY in environment). If that fails,
    # fall back to Windows SAPI (comtypes) so this script can produce a speech.wav
    # without external API keys.
    ok = try_use_groq(text, speech_file_path)
    if ok:
        print(f"Wrote speech using Groq to {speech_file_path}")
        sys.exit(0)

    # Fallback: local Windows TTS
    if os.name == "nt":
        try:
            synthesize_with_sapi(text, speech_file_path)
            print(f"Wrote speech using Windows SAPI to {speech_file_path}")
            sys.exit(0)
        except Exception as e:
            print("Local SAPI fallback failed:", e, file=sys.stderr)
            sys.exit(2)

    print("No usable TTS backend found (Groq unavailable or no API key, and SAPI not available).", file=sys.stderr)
    sys.exit(3)