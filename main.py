import disable_perth
import os
import json
import torch
import torchaudio as ta
import logging
import gc
import shutil
import uuid
import zipfile
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import FileResponse

from normalize import TextNormalizer
from chunking import smart_split_text
from audio_utils import to_audio_tensor, ensure_consistent_channels
from tts_client import generate_audio
from aligner import align_audio

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

app = FastAPI()

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def flush_memory():
    """Clears CUDA cache to prevent OOM errors."""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

def cleanup_files(directory_path):
    """Background task to remove temp files after response is sent."""
    try:
        shutil.rmtree(directory_path)
        logger.info(f"Cleaned up temporary directory: {directory_path}")
    except Exception as e:
        logger.error(f"Error cleaning up {directory_path}: {e}")

@app.post("/generate")
def generate_endpoint(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    reference_audio: UploadFile = File(...)
):
    # Create a unique temporary directory for this request
    request_id = str(uuid.uuid4())
    temp_dir = os.path.join(os.getcwd(), "temp_process", request_id)
    os.makedirs(temp_dir, exist_ok=True)

    try:
        logger.info(f"Starting request {request_id} on device: {DEVICE}")

        # 1. Save the uploaded reference audio
        ref_audio_path = os.path.join(temp_dir, "reference.wav")
        with open(ref_audio_path, "wb") as buffer:
            shutil.copyfileobj(reference_audio.file, buffer)

        # 2. Normalize Text
        logger.info("Normalizing text...")
        norm_text = TextNormalizer.normalize_math_and_symbols(text)
        
        # 3. Chunk Text
        chunks = smart_split_text(norm_text)
        logger.info(f"Text split into {len(chunks)} chunks.")

        # 4. Generate Audio (TTS)
        # Note: This is a heavy blocking operation. In a production async env, 
        # this might block the event loop, but standard def (not async def) 
        # in FastAPI runs in a threadpool, which is what we want here.
        audio_segments, sr = generate_audio(chunks, DEVICE, ref_audio_path)
        
        # 5. Process Audio Tensors
        audio_segments = [to_audio_tensor(w).cpu() for w in audio_segments]
        audio_segments = ensure_consistent_channels(audio_segments)
        full_audio = torch.cat(audio_segments, dim=1)
        
        # Normalize volume
        full_audio = full_audio / full_audio.abs().max()

        # 6. Save Generated WAV
        output_wav_path = os.path.join(temp_dir, "output.wav")
        ta.save(output_wav_path, full_audio, sr)
        
        # Flush memory before running Whisper
        flush_memory()

        # 7. Align Audio (Whisper)
        logger.info("Aligning audio (Whisper)...")
        segments = align_audio(output_wav_path, DEVICE)
        
        output_json_path = os.path.join(temp_dir, "output.json")
        with open(output_json_path, "w") as f:
            json.dump(segments, f, indent=2)

        # 8. Zip the results
        zip_filename = f"result_{request_id}.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(output_wav_path, arcname="output.wav")
            zipf.write(output_json_path, arcname="output.json")

        # Flush memory after completion
        flush_memory()

        # 9. Return the Zip File
        # We register a background task to delete the folder after the file is sent
        background_tasks.add_task(cleanup_files, temp_dir)
        
        return FileResponse(
            zip_path, 
            media_type='application/zip', 
            filename=zip_filename
        )

    except Exception as e:
        # Clean up if error occurs
        shutil.rmtree(temp_dir, ignore_errors=True)
        flush_memory()
        logger.error(f"Error processing request: {str(e)}")
        # Re-raise so FastAPI returns a 500 error
        raise e