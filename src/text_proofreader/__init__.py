"""
テキスト校正アプリケーション

テキストファイルを読み込み、誤字脱字、不適切な表現、
文脈の不整合を検出・指摘するPythonライブラリ。
"""

__version__ = "1.0.0"
__author__ = "Text Proofreader Team"

from .main import TextProofreader
from .reader import TextReader
from .reporter import Reporter

__all__ = ["TextProofreader", "TextReader", "Reporter"]