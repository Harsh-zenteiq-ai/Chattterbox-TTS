import numpy as np
import torch

def to_audio_tensor(wav) -> torch.Tensor:
    if isinstance(wav, list):
        wav = np.asarray(wav)
    if isinstance(wav, np.ndarray):
        wav = torch.from_numpy(wav)
    if not isinstance(wav, torch.Tensor):
        raise TypeError(f"Unsupported audio type: {type(wav)}")
    wav = wav.float()
    if wav.ndim == 1:
        wav = wav.unsqueeze(0)
    elif wav.ndim == 2:
        if wav.shape[0] > wav.shape[1] and wav.shape[0] > 8000:
            wav = wav.T
    else:
        raise ValueError("Audio tensor must be 1D or 2D")
    return wav

def ensure_consistent_channels(segments: list[torch.Tensor]) -> list[torch.Tensor]:
    if not segments:
        return segments
    channels = [s.shape[0] for s in segments if isinstance(s, torch.Tensor)]
    if all(c == channels[0] for c in channels):
        return segments
    mono_segments = []
    for s in segments:
        if s.shape[0] == 1:
            mono_segments.append(s)
        else:
            mono_segments.append(s.mean(dim=0, keepdim=True))
    return mono_segments
