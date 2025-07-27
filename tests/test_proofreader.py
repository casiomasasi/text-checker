"""
テキスト校正アプリケーションのテストスクリプト

基本的な動作確認を行う。
"""

import sys
from pathlib import Path

# 親ディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from text_proofreader.main import TextProofreader


def test_sample_text():
    """サンプルテキストの校正テスト"""
    print("=== テキスト校正アプリケーション テスト ===")
    
    # テストファイルのパス
    test_file = Path(__file__).parent / "sample_text.txt"
    
    if not test_file.exists():
        print(f"テストファイルが見つかりません: {test_file}")
        return False
    
    # 校正アプリケーションを初期化
    proofreader = TextProofreader()
    
    try:
        # ファイル情報を取得
        print("\\n1. ファイル情報の取得:")
        file_info = proofreader.get_file_info(str(test_file))
        for key, value in file_info.items():
            print(f"  {key}: {value}")
        
        # 校正チェックを実行
        print("\\n2. 校正チェックの実行:")
        result = proofreader.check_file(str(test_file))
        
        if result['success']:
            print(f"校正完了: {len(result['errors'])} 件の問題を検出")
            
            # サマリーを表示
            print("\\n3. サマリー:")
            proofreader.print_summary()
            
            # 検出されたエラーの詳細を表示
            print("\\n4. 検出されたエラーの詳細:")
            for i, error in enumerate(result['errors'][:10], 1):  # 最初の10件のみ表示
                print(f"  {i}. 行{error.get('line', 0)}列{error.get('column', 0)}: "
                      f"\"{error.get('original', '')}\" → "
                      f"\"{error.get('correction', error.get('suggestion', ''))}\" "
                      f"({error.get('description', '')})")
            
            if len(result['errors']) > 10:
                print(f"  ... 他 {len(result['errors']) - 10} 件")
            
            # レポート生成
            print("\\n5. レポート生成:")
            output_path = Path("data") / "test_report.xlsx"
            output_path.parent.mkdir(exist_ok=True)
            
            report_path = proofreader.generate_report(str(output_path))
            print(f"レポート生成完了: {report_path}")
            
            return True
        else:
            print(f"校正処理に失敗: {result.get('error', 'unknown error')}")
            return False
            
    except Exception as e:
        print(f"テスト実行中にエラー: {e}")
        return False


def test_individual_checkers():
    """個別チェッカーのテスト"""
    print("\\n=== 個別チェッカーテスト ===")
    
    from text_proofreader.checkers import TypoChecker, ExpressionChecker, ContextChecker
    
    test_text = "私わ学生です。記憶を取ることができます。了解しました。"
    
    # 誤字脱字チェッカーのテスト
    print("\\n1. 誤字脱字チェッカー:")
    typo_checker = TypoChecker()
    typo_errors = typo_checker.check_all_typos(test_text)
    print(f"  検出件数: {len(typo_errors)} 件")
    for error in typo_errors:
        print(f"    {error.get('original', '')} → {error.get('correction', '')}")
    
    # 不適切表現チェッカーのテスト
    print("\\n2. 不適切表現チェッカー:")
    expression_checker = ExpressionChecker()
    expression_errors = expression_checker.check_all_expressions(test_text)
    print(f"  検出件数: {len(expression_errors)} 件")
    for error in expression_errors:
        print(f"    {error.get('original', '')} → {error.get('suggestion', '')}")
    
    # 文脈整合性チェッカーのテスト
    print("\\n3. 文脈整合性チェッカー:")
    context_checker = ContextChecker()
    context_errors = context_checker.check_all_context(test_text)
    print(f"  検出件数: {len(context_errors)} 件")
    for error in context_errors:
        print(f"    {error.get('original', '')} → {error.get('suggestion', '')}")


if __name__ == "__main__":
    # 依存関係の確認
    try:
        import pandas
        import openpyxl
        import chardet
        print("必要な依存関係が確認できました。")
    except ImportError as e:
        print(f"依存関係が不足しています: {e}")
        print("pip install pandas openpyxl chardet を実行してください。")
        sys.exit(1)
    
    # メインテストを実行
    success = test_sample_text()
    
    # 個別チェッカーのテスト
    test_individual_checkers()
    
    if success:
        print("\\n=== テスト完了 ===")
        print("すべてのテストが正常に完了しました。")
    else:
        print("\\n=== テスト失敗 ===")
        print("一部のテストで問題が発生しました。")
        sys.exit(1)