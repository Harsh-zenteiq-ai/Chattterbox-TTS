packages required : chatterbox-tts
                    fastapi , uvicorn 
                    whisper_timestamped
                    numpy == 1.25.2 # specific version to avoid compatibility issues
                    ffmeg # sudo apt install ffmpeg
                    num2words

models used :
- Whisper Timestamped : for audio transcription and timestamping
- Chatterbox TTS : for text-to-speech synthesis 

commad to run the server : uvicorn main:app