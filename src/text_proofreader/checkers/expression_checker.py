"""
不適切表現チェック機能

テキスト内の不適切な表現、敬語の誤用、冗長表現などを検出する。
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ExpressionChecker:
    """不適切表現チェックを行うクラス"""
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        ExpressionCheckerを初期化
        
        Args:
            rules_path: ルールファイルのパス（指定しない場合はデフォルトを使用）
        """
        if rules_path is None:
            rules_path = Path(__file__).parent.parent / "rules" / "expression_rules.json"
        
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
    
    def check_inappropriate_expressions(self, text: str) -> List[Dict]:
        """
        不適切表現をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        inappropriate_rules = self.rules.get('inappropriate_expressions', {})
        
        # 差別的表現のチェック
        discriminatory_rules = inappropriate_rules.get('discriminatory', {})
        for word, rule in discriminatory_rules.items():
            pattern = rule.get('pattern', word)
            suggestion = rule.get('suggestion', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'inappropriate_expression',
                    'subtype': 'discriminatory',
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity
                })
        
        return errors
    
    def check_honorific_errors(self, text: str) -> List[Dict]:
        """
        敬語の誤用をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        honorific_rules = self.rules.get('inappropriate_expressions', {}).get('inappropriate_honorifics', {})
        
        for error_type, rule in honorific_rules.items():
            pattern = rule.get('pattern', '')
            suggestion = rule.get('suggestion', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'honorific_error',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity
                })
        
        return errors
    
    def check_inappropriate_abbreviations(self, text: str) -> List[Dict]:
        """
        不適切な略語・口語表現をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        abbreviation_rules = self.rules.get('inappropriate_expressions', {}).get('inappropriate_abbreviations', {})
        
        for error_type, rule in abbreviation_rules.items():
            pattern = rule.get('pattern', '')
            suggestion = rule.get('suggestion', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'inappropriate_abbreviation',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity
                })
        
        return errors
    
    def check_redundant_expressions(self, text: str) -> List[Dict]:
        """
        冗長表現をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        redundant_rules = self.rules.get('inappropriate_expressions', {}).get('redundant_expressions', {})
        
        for error_type, rule in redundant_rules.items():
            pattern = rule.get('pattern', '')
            suggestion = rule.get('suggestion', '')
            severity = rule.get('severity', 'low')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'redundant_expression',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity
                })
        
        return errors
    
    def check_style_inconsistency(self, text: str) -> List[Dict]:
        """
        文体の不統一をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        style_rules = self.rules.get('style_inconsistency', {})
        
        # 敬語と常体の混在チェック
        formality_rules = style_rules.get('formality_mixing', {})
        for error_type, rule in formality_rules.items():
            pattern = rule.get('pattern', '')
            suggestion = rule.get('suggestion', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'style_inconsistency',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity
                })
        
        # 数字表記の混在チェック
        number_rules = style_rules.get('number_notation', {})
        for error_type, rule in number_rules.items():
            pattern = rule.get('pattern', '')
            suggestion = rule.get('suggestion', '')
            severity = rule.get('severity', 'low')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'style_inconsistency',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity
                })
        
        return errors
    
    def check_word_choice(self, text: str) -> List[Dict]:
        """
        語彙選択の問題をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        word_choice_rules = self.rules.get('word_choice', {})
        
        for error_type, rule in word_choice_rules.items():
            pattern = rule.get('pattern', '')
            suggestion = rule.get('suggestion', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'word_choice',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity
                })
        
        return errors
    
    def check_all_expressions(self, text: str) -> List[Dict]:
        """
        すべての表現チェックを実行
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        all_errors = []
        
        # 各種チェックを実行
        all_errors.extend(self.check_inappropriate_expressions(text))
        all_errors.extend(self.check_honorific_errors(text))
        all_errors.extend(self.check_inappropriate_abbreviations(text))
        all_errors.extend(self.check_redundant_expressions(text))
        all_errors.extend(self.check_style_inconsistency(text))
        all_errors.extend(self.check_word_choice(text))
        
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
        suggestion = error.get('suggestion', '')
        description = error.get('description', '')
        
        message = f"行{line}列{column}: \"{original}\" → \"{suggestion}\" ({description})"
        
        return message