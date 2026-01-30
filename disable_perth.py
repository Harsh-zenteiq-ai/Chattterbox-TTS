#due to package dependency issues, perth watermarking is disabled. 

import sys, types

class DummyWatermarker:
    def __init__(self, *a, **k):
        pass

    def apply_watermark(self, wav, sample_rate=None):
        return wav

    def __call__(self, *a, **k):
        return None

dummy_module = types.SimpleNamespace(
    PerthImplicitWatermarker=DummyWatermarker
)

sys.modules["perth"] = dummy_module
