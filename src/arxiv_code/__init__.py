"""
arxiv-code — Emergent arXiv TeX decompiler and algorithmic code extractor.
"""

__version__ = "0.1.0"
__author__ = "ToxicWind"

from .client import ArxivClient
from .extractor import TexExtractor
from .miner import CodeMiner

__all__ = ["ArxivClient", "TexExtractor", "CodeMiner"]
