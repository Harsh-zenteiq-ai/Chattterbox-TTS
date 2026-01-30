import whisper_timestamped as whisper

def align_audio(path, device):
    model = whisper.load_model("base.en", device=device)
    audio_loaded = whisper.load_audio(path)
    try:
        result = whisper.transcribe(
                model, 
                audio_loaded, 
                language="en", 
                temperature=0,
                beam_size=1,
                condition_on_previous_text=False
            )
    except Exception:
        result = whisper.transcribe(model, path, language="en")
    return result.get("segments", [])
