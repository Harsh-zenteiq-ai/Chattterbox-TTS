import torch
import logging
from chatterbox.tts import ChatterboxTTS

# Setup logger
logger = logging.getLogger("uvicorn")

def generate_audio(chunks, device, audio_prompt_path):
    audio_segments = []
    # Default sr, will be overwritten by model.sr if available
    sr = 24000 
    
    logger.info("Loading TTS Model...")
    tts_model = ChatterboxTTS.from_pretrained(device=device)
    sr = getattr(tts_model, "sr", sr)

    silence_template = None
    total_chunks = len(chunks)

    with torch.no_grad():
        for i, chunk in enumerate(chunks):
            # Log progress
            logger.info(f"Processing chunk {i + 1}/{total_chunks}")
            
            wav_raw = tts_model.generate(chunk, audio_prompt_path=audio_prompt_path)
            wav = wav_raw
            
            if silence_template is None:
                # Create a short silence tensor based on sample rate
                silence_template = torch.zeros(wav.shape[0], int(sr * 0.3))
            
            audio_segments.append(wav)
            
            # Add silence between chunks
            if i < len(chunks) - 1:
                audio_segments.append(silence_template)
    
    # Cleanup model to free VRAM
    del tts_model
    return audio_segments, sr