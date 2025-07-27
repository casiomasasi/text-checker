"""
テキストファイル読み込み機能

様々な形式のテキストファイルを読み込み、
エンコーディングを自動判定して統一された形式で返す。
"""

import os
import chardet
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union


class TextReader:
    """テキストファイル読み込みクラス"""
    
    SUPPORTED_EXTENSIONS = {'.txt', '.md', '.csv', '.log'}
    DEFAULT_ENCODING = 'utf-8'
    CHUNK_SIZE = 8192  # チャンク読み込みサイズ
    
    def __init__(self):
        self.current_file_path: Optional[Path] = None
        self.current_encoding: Optional[str] = None
        
    def detect_encoding(self, file_path: Union[str, Path]) -> str:
        """
        ファイルのエンコーディングを自動判定
        
        Args:
            file_path: ファイルパス
            
        Returns:
            検出されたエンコーディング名
        """
        file_path = Path(file_path)
        
        try:
            with open(file_path, 'rb') as f:
                # ファイルの最初の部分を読み込んで判定
                raw_data = f.read(min(32768, os.path.getsize(file_path)))
                
            detection_result = chardet.detect(raw_data)
            encoding = detection_result.get('encoding', self.DEFAULT_ENCODING)
            confidence = detection_result.get('confidence', 0.0)
            
            # 信頼度が低い場合はデフォルトエンコーディングを使用
            if confidence < 0.7:
                encoding = self.DEFAULT_ENCODING
                
            return encoding
            
        except Exception as e:
            print(f"エンコーディング判定エラー: {e}")
            return self.DEFAULT_ENCODING
    
    def read_file(self, file_path: Union[str, Path]) -> Dict[str, Union[str, List[str], Dict]]:
        """
        テキストファイルを読み込み
        
        Args:
            file_path: 読み込むファイルのパス
            
        Returns:
            読み込み結果の辞書
            {
                'content': str,           # ファイル全体の内容
                'lines': List[str],       # 行ごとのリスト
                'metadata': Dict          # メタデータ
            }
        """
        file_path = Path(file_path)
        
        # ファイル存在チェック
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        # 拡張子チェック
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"サポートされていないファイル形式: {file_path.suffix}")
        
        # エンコーディング判定
        encoding = self.detect_encoding(file_path)
        self.current_file_path = file_path
        self.current_encoding = encoding
        
        try:
            # ファイル読み込み
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                lines = content.splitlines()
            
            # メタデータ作成
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'encoding': encoding,
                'line_count': len(lines),
                'char_count': len(content),
                'extension': file_path.suffix.lower()
            }
            
            return {
                'content': content,
                'lines': lines,
                'metadata': metadata
            }
            
        except UnicodeDecodeError as e:
            # エンコーディングエラーの場合、他のエンコーディングを試す
            encodings_to_try = ['utf-8', 'shift_jis', 'euc-jp', 'iso-2022-jp']
            
            for enc in encodings_to_try:
                if enc == encoding:
                    continue
                    
                try:
                    with open(file_path, 'r', encoding=enc) as f:
                        content = f.read()
                        lines = content.splitlines()
                    
                    self.current_encoding = enc
                    
                    metadata = {
                        'file_path': str(file_path),
                        'file_name': file_path.name,
                        'file_size': file_path.stat().st_size,
                        'encoding': enc,
                        'line_count': len(lines),
                        'char_count': len(content),
                        'extension': file_path.suffix.lower()
                    }
                    
                    return {
                        'content': content,
                        'lines': lines,
                        'metadata': metadata
                    }
                    
                except UnicodeDecodeError:
                    continue
            
            raise ValueError(f"ファイルを読み込めませんでした: {file_path}")
        
        except Exception as e:
            raise Exception(f"ファイル読み込みエラー: {e}")
    
    def read_large_file(self, file_path: Union[str, Path]) -> Dict[str, Union[str, List[str], Dict]]:
        """
        大容量ファイルをチャンク単位で読み込み
        
        Args:
            file_path: 読み込むファイルのパス
            
        Returns:
            読み込み結果の辞書
        """
        file_path = Path(file_path)
        
        # ファイルサイズチェック（1MB以上は大容量として扱う）
        if file_path.stat().st_size < 1024 * 1024:
            return self.read_file(file_path)
        
        # エンコーディング判定
        encoding = self.detect_encoding(file_path)
        self.current_file_path = file_path
        self.current_encoding = encoding
        
        try:
            content_chunks = []
            lines = []
            
            with open(file_path, 'r', encoding=encoding) as f:
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    content_chunks.append(chunk)
            
            content = ''.join(content_chunks)
            lines = content.splitlines()
            
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'encoding': encoding,
                'line_count': len(lines),
                'char_count': len(content),
                'extension': file_path.suffix.lower(),
                'large_file': True
            }
            
            return {
                'content': content,
                'lines': lines,
                'metadata': metadata
            }
            
        except Exception as e:
            raise Exception(f"大容量ファイル読み込みエラー: {e}")
    
    def read_csv_text_column(self, file_path: Union[str, Path], 
                           text_column: str = 'text') -> Dict[str, Union[List[str], Dict]]:
        """
        CSVファイルの特定の列をテキストとして読み込み
        
        Args:
            file_path: CSVファイルのパス
            text_column: テキストが含まれる列名
            
        Returns:
            読み込み結果の辞書
        """
        import csv
        
        file_path = Path(file_path)
        encoding = self.detect_encoding(file_path)
        
        try:
            text_lines = []
            
            with open(file_path, 'r', encoding=encoding, newline='') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    if text_column in row and row[text_column]:
                        text_lines.append(row[text_column].strip())
            
            content = '\n'.join(text_lines)
            
            metadata = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'file_size': file_path.stat().st_size,
                'encoding': encoding,
                'line_count': len(text_lines),
                'char_count': len(content),
                'extension': file_path.suffix.lower(),
                'csv_column': text_column
            }
            
            return {
                'content': content,
                'lines': text_lines,
                'metadata': metadata
            }
            
        except Exception as e:
            raise Exception(f"CSV読み込みエラー: {e}")
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Union[str, int]]:
        """
        ファイル情報を取得（読み込まずに）
        
        Args:
            file_path: ファイルパス
            
        Returns:
            ファイル情報の辞書
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")
        
        stat = file_path.stat()
        encoding = self.detect_encoding(file_path)
        
        return {
            'file_path': str(file_path),
            'file_name': file_path.name,
            'file_size': stat.st_size,
            'encoding': encoding,
            'extension': file_path.suffix.lower(),
            'is_supported': file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS,
            'is_large_file': stat.st_size > 1024 * 1024
        }