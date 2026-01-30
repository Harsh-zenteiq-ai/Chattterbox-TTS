# tests/test_audio_utils.py
import numpy as np
import torch
from src.audio_utils import to_audio_tensor, ensure_consistent_channels

def test_to_audio_tensor_from_numpy():
    arr = np.random.randn(16000).astype(np.float32)
    t = to_audio_tensor(arr)
    assert isinstance(t, torch.Tensor)
    assert t.ndim == 2
    assert t.shape[0] == 1

def test_ensure_channels_mono_to_stereo():
    mono = torch.randn(1, 16000)
    out = ensure_consistent_channels([mono], target_channels=2)
    assert out[0].shape[0] == 2

def test_ensure_channels_stereo_to_mono():
    stereo = torch.randn(2, 16000)
    out = ensure_consistent_channels([stereo], target_channels=1)
    assert out[0].shape[0] == 1
