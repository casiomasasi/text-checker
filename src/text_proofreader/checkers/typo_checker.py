"""
誤字脱字チェック機能

テキスト内の誤字脱字を検出し、修正案を提案する。
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class TypoChecker:
    """誤字脱字チェックを行うクラス"""
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        TypoCheckerを初期化
        
        Args:
            rules_path: ルールファイルのパス（指定しない場合はデフォルトを使用）
        """
        if rules_path is None:
            rules_path = Path(__file__).parent.parent / "rules" / "typo_rules.json"
        
        self.rules_path = Path(rules_path)
        self.rules = self._load_rules()
        
    def _load_rules(self) -> Dict:
        """
        ルールファイルを読み込み
        
        Returns:
            ルール辞書
        """
        try:
            with open(self.rules_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"ルールファイル読み込みエラー: {e}")
            return {}
    
    def check_hiragana_katakana_errors(self, text: str) -> List[Dict]:
        """
        ひらがな・カタカナの誤字をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        rules = self.rules.get('hiragana_katakana_errors', {})
        
        for error_type, rule in rules.items():
            pattern = rule.get('pattern', '')
            correction = rule.get('correction', '')
            description = rule.get('description', '')
            examples = rule.get('examples', [])
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'hiragana_katakana_error',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'correction': correction,
                    'description': description,
                    'examples': examples,
                    'severity': 'high'
                })
        
        return errors
    
    def check_kanji_conversion_errors(self, text: str) -> List[Dict]:
        """
        漢字変換誤りをチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        rules = self.rules.get('kanji_conversion_errors', {})
        
        for error_type, rule in rules.items():
            pattern = rule.get('pattern', '')
            correction = rule.get('correction', '')
            description = rule.get('description', '')
            examples = rule.get('examples', [])
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'kanji_conversion_error',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'correction': correction,
                    'description': description,
                    'examples': examples,
                    'severity': 'high'
                })
        
        return errors
    
    def check_typing_errors(self, text: str) -> List[Dict]:
        """
        タイプミスをチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        rules = self.rules.get('typing_errors', {})
        
        for error_type, rule in rules.items():
            pattern = rule.get('pattern', '')
            correction = rule.get('correction', '')
            description = rule.get('description', '')
            examples = rule.get('examples', [])
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                # 重複文字の場合は修正案を生成
                if error_type == 'duplicate_chars':
                    correction_text = re.sub(r'([あ-んア-ンa-zA-Z])\1{2,}', r'\1', error_text)
                else:
                    correction_text = correction
                
                errors.append({
                    'type': 'typing_error',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'correction': correction_text,
                    'description': description,
                    'examples': examples,
                    'severity': 'medium'
                })
        
        return errors
    
    def check_okurigana_errors(self, text: str) -> List[Dict]:
        """
        送り仮名の誤りをチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        rules = self.rules.get('okurigana_errors', {})
        
        for error_type, rule in rules.items():
            pattern = rule.get('pattern', '')
            correction = rule.get('correction', '')
            description = rule.get('description', '')
            examples = rule.get('examples', [])
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'okurigana_error',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'correction': correction,
                    'description': description,
                    'examples': examples,
                    'severity': 'medium'
                })
        
        return errors
    
    def check_all_typos(self, text: str) -> List[Dict]:
        """
        すべての誤字脱字チェックを実行
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        all_errors = []
        
        # 各種チェックを実行
        all_errors.extend(self.check_hiragana_katakana_errors(text))
        all_errors.extend(self.check_kanji_conversion_errors(text))
        all_errors.extend(self.check_typing_errors(text))
        all_errors.extend(self.check_okurigana_errors(text))
        
        # 位置でソート
        all_errors.sort(key=lambda x: x['position'][0])
        
        return all_errors
    
    def get_line_and_column(self, text: str, position: int) -> Tuple[int, int]:
        """
        文字位置から行番号と列番号を取得
        
        Args:
            text: 全体のテキスト
            position: 文字位置
            
        Returns:
            (行番号, 列番号) のタプル（1始まり）
        """
        lines = text[:position].split('\n')
        line_number = len(lines)
        column_number = len(lines[-1]) + 1
        
        return line_number, column_number
    
    def add_position_info(self, text: str, errors: List[Dict]) -> List[Dict]:
        """
        エラー情報に行・列番号を追加
        
        Args:
            text: 全体のテキスト
            errors: エラーリスト
            
        Returns:
            行・列情報が追加されたエラーリスト
        """
        for error in errors:
            start_pos = error['position'][0]
            line, column = self.get_line_and_column(text, start_pos)
            error['line'] = line
            error['column'] = column
        
        return errors
    
    def format_error_message(self, error: Dict) -> str:
        """
        エラーメッセージをフォーマット
        
        Args:
            error: エラー辞書
            
        Returns:
            フォーマットされたメッセージ
        """
        line = error.get('line', 0)
        column = error.get('column', 0)
        original = error.get('original', '')
        correction = error.get('correction', '')
        description = error.get('description', '')
        
        message = f"行{line}列{column}: \"{original}\" → \"{correction}\" ({description})"
        
        return message