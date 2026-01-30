# tests/test_normalize.py
import pytest
from src.normalize import TextNormalizer

def test_complement_and_ordered_pair_protection():
    tn = TextNormalizer()
    src = "Welcome to MCP'. Consider (x, y) and (A,B). Also X^c and AB''."
    out = tn.normalize(src)
    # compliments expanded
    assert "complement" in out
    # ordered pairs should have comma preserved when restored
    assert "(x, y)" in out or "(x, y)" in out.replace("  ", " ")

def test_symbol_map():
    tn = TextNormalizer()
    s = "A ∪ B × C → D …"
    out = tn.normalize(s)
    assert "union" in out
    assert "cross" in out
    assert "arrow" in out
    assert "..." in out or "..." in out
