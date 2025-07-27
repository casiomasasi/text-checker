"""
文脈整合性チェック機能

テキスト内の文脈の不整合、論理的問題、構造的問題を検出する。
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ContextChecker:
    """文脈整合性チェックを行うクラス"""
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        ContextCheckerを初期化
        
        Args:
            rules_path: ルールファイルのパス（指定しない場合はデフォルトを使用）
        """
        if rules_path is None:
            rules_path = Path(__file__).parent.parent / "rules" / "context_rules.json"
        
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
    
    def check_pronoun_reference(self, text: str) -> List[Dict]:
        """
        代名詞の指示対象の曖昧さをチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        context_rules = self.rules.get('context_consistency', {})
        pronoun_rules = context_rules.get('pronoun_reference', {})
        
        for error_type, rule in pronoun_rules.items():
            pattern = rule.get('pattern', '')
            check_type = rule.get('check_type', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                # 代名詞の前後をチェックして指示対象の明確性を判断
                is_ambiguous = self._check_pronoun_clarity(text, start, end)
                
                if is_ambiguous:
                    errors.append({
                        'type': 'context_consistency',
                        'subtype': error_type,
                        'position': (start, end),
                        'original': error_text,
                        'suggestion': '指示対象を明確にする',
                        'description': description,
                        'severity': severity,
                        'check_type': check_type
                    })
        
        return errors
    
    def _check_pronoun_clarity(self, text: str, start: int, end: int) -> bool:
        """
        代名詞の指示対象が明確かどうかを判断
        
        Args:
            text: 全体のテキスト
            start: 代名詞の開始位置
            end: 代名詞の終了位置
            
        Returns:
            True if ambiguous, False if clear
        """
        # 簡易的な判断ロジック
        # 前の文に名詞が1つしかない場合は明確、複数ある場合は曖昧
        pronoun = text[start:end]
        
        # 前の文を取得
        sentences = re.split(r'[。！？]', text[:start])
        if len(sentences) < 2:
            return False
        
        previous_sentence = sentences[-2]
        
        # 名詞らしきものをカウント（簡易的）
        nouns = re.findall(r'[一-龯]{2,}', previous_sentence)
        
        # 複数の名詞がある場合は曖昧とみなす
        return len(nouns) > 1
    
    def check_tense_consistency(self, text: str) -> List[Dict]:
        """
        時制の整合性をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        context_rules = self.rules.get('context_consistency', {})
        tense_rules = context_rules.get('tense_consistency', {})
        
        for error_type, rule in tense_rules.items():
            pattern = rule.get('pattern', '')
            check_type = rule.get('check_type', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                errors.append({
                    'type': 'context_consistency',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': '時制を統一する',
                    'description': description,
                    'severity': severity,
                    'check_type': check_type
                })
        
        return errors
    
    def check_logical_flow(self, text: str) -> List[Dict]:
        """
        論理的な流れをチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        context_rules = self.rules.get('context_consistency', {})
        logical_rules = context_rules.get('logical_flow', {})
        
        for error_type, rule in logical_rules.items():
            pattern = rule.get('pattern', '')
            check_type = rule.get('check_type', '')
            severity = rule.get('severity', 'high')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                suggestion = self._get_logical_suggestion(error_type)
                
                errors.append({
                    'type': 'logical_flow',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity,
                    'check_type': check_type
                })
        
        return errors
    
    def _get_logical_suggestion(self, error_type: str) -> str:
        """
        論理エラーの種類に応じた修正提案を取得
        
        Args:
            error_type: エラーの種類
            
        Returns:
            修正提案
        """
        suggestions = {
            'conclusion_without_reason': '結論の前に根拠を明記する',
            'contradiction': '矛盾する内容を確認し、整合性を取る'
        }
        
        return suggestions.get(error_type, '論理的な整合性を確認する')
    
    def check_coherence(self, text: str) -> List[Dict]:
        """
        文章の一貫性をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        context_rules = self.rules.get('context_consistency', {})
        coherence_rules = context_rules.get('coherence', {})
        
        for error_type, rule in coherence_rules.items():
            pattern = rule.get('pattern', '')
            check_type = rule.get('check_type', '')
            severity = rule.get('severity', 'low')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                suggestion = self._get_coherence_suggestion(error_type)
                
                errors.append({
                    'type': 'coherence',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity,
                    'check_type': check_type
                })
        
        return errors
    
    def _get_coherence_suggestion(self, error_type: str) -> str:
        """
        一貫性エラーの種類に応じた修正提案を取得
        
        Args:
            error_type: エラーの種類
            
        Returns:
            修正提案
        """
        suggestions = {
            'topic_shift': '話題転換をより自然にする',
            'repetitive_content': '重複する内容を削除または統合する'
        }
        
        return suggestions.get(error_type, '文章の一貫性を改善する')
    
    def check_structure_issues(self, text: str) -> List[Dict]:
        """
        文章構造の問題をチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        structure_rules = self.rules.get('structure_issues', {})
        
        # 段落構造のチェック
        paragraph_rules = structure_rules.get('paragraph_structure', {})
        for error_type, rule in paragraph_rules.items():
            pattern = rule.get('pattern', '')
            check_type = rule.get('check_type', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                suggestion = self._get_structure_suggestion(error_type)
                
                errors.append({
                    'type': 'structure_issue',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity,
                    'check_type': check_type
                })
        
        # 句点のチェック
        punctuation_rules = structure_rules.get('punctuation', {})
        for error_type, rule in punctuation_rules.items():
            pattern = rule.get('pattern', '')
            check_type = rule.get('check_type', '')
            severity = rule.get('severity', 'medium')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                suggestion = self._get_punctuation_suggestion(error_type)
                
                errors.append({
                    'type': 'punctuation_issue',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity,
                    'check_type': check_type
                })
        
        return errors
    
    def _get_structure_suggestion(self, error_type: str) -> str:
        """
        構造エラーの種類に応じた修正提案を取得
        """
        suggestions = {
            'long_sentences': '文を短く分割する',
            'short_paragraphs': '段落を統合するか、内容を追加する'
        }
        
        return suggestions.get(error_type, '文章構造を改善する')
    
    def _get_punctuation_suggestion(self, error_type: str) -> str:
        """
        句点エラーの種類に応じた修正提案を取得
        """
        suggestions = {
            'missing_periods': '文末に句点を追加する',
            'excessive_punctuation': '過度な句点・感嘆符を削除する'
        }
        
        return suggestions.get(error_type, '句点の使用を改善する')
    
    def check_readability(self, text: str) -> List[Dict]:
        """
        読みやすさをチェック
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        errors = []
        readability_rules = self.rules.get('readability', {})
        complexity_rules = readability_rules.get('complexity', {})
        
        for error_type, rule in complexity_rules.items():
            pattern = rule.get('pattern', '')
            check_type = rule.get('check_type', '')
            severity = rule.get('severity', 'low')
            description = rule.get('description', '')
            
            matches = re.finditer(pattern, text)
            for match in matches:
                start, end = match.span()
                error_text = match.group()
                
                suggestion = self._get_readability_suggestion(error_type)
                
                errors.append({
                    'type': 'readability',
                    'subtype': error_type,
                    'position': (start, end),
                    'original': error_text,
                    'suggestion': suggestion,
                    'description': description,
                    'severity': severity,
                    'check_type': check_type
                })
        
        return errors
    
    def _get_readability_suggestion(self, error_type: str) -> str:
        """
        読みやすさエラーの種類に応じた修正提案を取得
        """
        suggestions = {
            'difficult_kanji': '漢字とひらがなのバランスを調整する',
            'katakana_overuse': 'カタカナの使用を控えめにする'
        }
        
        return suggestions.get(error_type, '読みやすさを改善する')
    
    def check_all_context(self, text: str) -> List[Dict]:
        """
        すべての文脈チェックを実行
        
        Args:
            text: チェック対象のテキスト
            
        Returns:
            検出結果のリスト
        """
        all_errors = []
        
        # 各種チェックを実行
        all_errors.extend(self.check_pronoun_reference(text))
        all_errors.extend(self.check_tense_consistency(text))
        all_errors.extend(self.check_logical_flow(text))
        all_errors.extend(self.check_coherence(text))
        all_errors.extend(self.check_structure_issues(text))
        all_errors.extend(self.check_readability(text))
        
        # 位置でソート
        all_errors.sort(key=lambda x: x['position'][0])
        
        return all_errors
    
    def get_line_and_column(self, text: str, position: int) -> Tuple[int, int]:
        """
        文字位置から行番号と列番号を取得
        """
        lines = text[:position].split('\n')
        line_number = len(lines)
        column_number = len(lines[-1]) + 1
        
        return line_number, column_number
    
    def add_position_info(self, text: str, errors: List[Dict]) -> List[Dict]:
        """
        エラー情報に行・列番号を追加
        """
        for error in errors:
            start_pos = error['position'][0]
            line, column = self.get_line_and_column(text, start_pos)
            error['line'] = line
            error['column'] = column
        
        return errors