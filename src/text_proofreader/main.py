"""
テキスト校正アプリケーション メインモジュール

全ての校正機能を統合し、CLIインターフェースを提供する。
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .reader import TextReader
from .checkers import TypoChecker, ExpressionChecker, ContextChecker
from .reporter import Reporter


class TextProofreader:
    """テキスト校正アプリケーションのメインクラス"""
    
    def __init__(self):
        """TextProofreaderを初期化"""
        self.reader = TextReader()
        self.typo_checker = TypoChecker()
        self.expression_checker = ExpressionChecker()
        self.context_checker = ContextChecker()
        self.reporter = Reporter()
        
    def check_file(self, file_path: str, 
                   check_typos: bool = True,
                   check_expressions: bool = True,
                   check_context: bool = True,
                   csv_column: Optional[str] = None) -> dict:
        """
        ファイルを校正チェック
        
        Args:
            file_path: 校正対象ファイルのパス
            check_typos: 誤字脱字チェックを実行するか
            check_expressions: 不適切表現チェックを実行するか
            check_context: 文脈整合性チェックを実行するか
            csv_column: CSVファイルの場合のテキスト列名
            
        Returns:
            校正結果の辞書
        """
        try:
            # ファイル読み込み
            print(f"ファイルを読み込み中: {file_path}")
            
            if csv_column and file_path.endswith('.csv'):
                file_data = self.reader.read_csv_text_column(file_path, csv_column)
            else:
                file_data = self.reader.read_file(file_path)
            
            text = file_data['content']
            metadata = file_data['metadata']
            
            print(f"読み込み完了: {metadata.get('char_count', 0)} 文字")
            
            # 校正チェック実行
            all_errors = []
            
            if check_typos:
                print("誤字脱字チェック実行中...")
                typo_errors = self.typo_checker.check_all_typos(text)
                typo_errors = self.typo_checker.add_position_info(text, typo_errors)
                all_errors.extend(typo_errors)
                print(f"誤字脱字: {len(typo_errors)} 件検出")
            
            if check_expressions:
                print("不適切表現チェック実行中...")
                expression_errors = self.expression_checker.check_all_expressions(text)
                expression_errors = self.expression_checker.add_position_info(text, expression_errors)
                all_errors.extend(expression_errors)
                print(f"不適切表現: {len(expression_errors)} 件検出")
            
            if check_context:
                print("文脈整合性チェック実行中...")
                context_errors = self.context_checker.check_all_context(text)
                context_errors = self.context_checker.add_position_info(text, context_errors)
                all_errors.extend(context_errors)
                print(f"文脈整合性: {len(context_errors)} 件検出")
            
            # 結果をレポーターに追加
            self.reporter.clear_results()
            self.reporter.add_results(all_errors, metadata)
            
            print(f"\n合計 {len(all_errors)} 件の問題を検出しました。")
            
            return {
                'success': True,
                'file_path': file_path,
                'errors': all_errors,
                'metadata': metadata,
                'summary': self.reporter.get_summary()
            }
            
        except Exception as e:
            error_msg = f"校正処理中にエラーが発生しました: {e}"
            print(error_msg)
            return {
                'success': False,
                'error': error_msg,
                'file_path': file_path
            }
    
    def generate_report(self, output_path: str) -> str:
        """
        Excelレポートを生成
        
        Args:
            output_path: 出力ファイルパス
            
        Returns:
            生成されたファイルのパス
        """
        try:
            print(f"レポートを生成中: {output_path}")
            report_path = self.reporter.generate_excel_report(output_path)
            print(f"レポート生成完了: {report_path}")
            return report_path
        except Exception as e:
            error_msg = f"レポート生成中にエラーが発生しました: {e}"
            print(error_msg)
            raise Exception(error_msg)
    
    def print_summary(self):
        """サマリーをコンソールに表示"""
        self.reporter.print_summary()
    
    def get_file_info(self, file_path: str) -> dict:
        """
        ファイル情報を取得（校正なし）
        
        Args:
            file_path: ファイルパス
            
        Returns:
            ファイル情報の辞書
        """
        try:
            return self.reader.get_file_info(file_path)
        except Exception as e:
            return {'error': str(e)}


def create_cli_parser():
    """コマンドライン引数のパーサーを作成"""
    parser = argparse.ArgumentParser(
        description='テキスト校正アプリケーション',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
使用例:
  python -m text_proofreader.main input.txt
  python -m text_proofreader.main input.txt -o report.xlsx
  python -m text_proofreader.main data.csv --csv-column text_column
  python -m text_proofreader.main input.txt --no-context --no-expressions
        '''
    )
    
    # 必須引数
    parser.add_argument(
        'input_file',
        help='校正対象のテキストファイル'
    )
    
    # オプション引数
    parser.add_argument(
        '-o', '--output',
        default=None,
        help='レポート出力ファイルパス（デフォルト: data/proofreading_report.xlsx）'
    )
    
    parser.add_argument(
        '--csv-column',
        default='text',
        help='CSVファイルの場合のテキスト列名（デフォルト: text）'
    )
    
    # チェック機能のON/OFF
    parser.add_argument(
        '--no-typos',
        action='store_true',
        help='誤字脱字チェックを無効にする'
    )
    
    parser.add_argument(
        '--no-expressions',
        action='store_true',
        help='不適切表現チェックを無効にする'
    )
    
    parser.add_argument(
        '--no-context',
        action='store_true',
        help='文脈整合性チェックを無効にする'
    )
    
    parser.add_argument(
        '--info-only',
        action='store_true',
        help='ファイル情報のみを表示（校正なし）'
    )
    
    parser.add_argument(
        '--no-report',
        action='store_true',
        help='Excelレポートを生成しない'
    )
    
    return parser


def main():
    """メイン関数"""
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # 入力ファイルの存在確認
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"エラー: ファイルが見つかりません: {input_path}")
        sys.exit(1)
    
    # アプリケーション初期化
    proofreader = TextProofreader()
    
    # ファイル情報のみの表示
    if args.info_only:
        file_info = proofreader.get_file_info(args.input_file)
        if 'error' in file_info:
            print(f"エラー: {file_info['error']}")
            sys.exit(1)
        
        print("=== ファイル情報 ===")
        for key, value in file_info.items():
            print(f"{key}: {value}")
        sys.exit(0)
    
    # 校正チェック実行
    result = proofreader.check_file(
        args.input_file,
        check_typos=not args.no_typos,
        check_expressions=not args.no_expressions,
        check_context=not args.no_context,
        csv_column=args.csv_column if input_path.suffix.lower() == '.csv' else None
    )
    
    if not result['success']:
        print(f"エラー: {result['error']}")
        sys.exit(1)
    
    # サマリー表示
    proofreader.print_summary()
    
    # レポート生成
    if not args.no_report:
        # 出力パスの決定
        if args.output:
            output_path = args.output
        else:
            # デフォルトの出力パス
            output_dir = Path('data')
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / 'proofreading_report.xlsx'
        
        try:
            report_path = proofreader.generate_report(output_path)
            print(f"\n詳細レポートは以下のファイルに出力されました:")
            print(f"{report_path}")
        except Exception as e:
            print(f"\nレポート生成に失敗しました: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()