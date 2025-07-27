#!/usr/bin/env python3
"""
CLI版テキスト校正アプリケーションのテストスクリプト

基本的な校正機能をテストします。
"""

import sys
from pathlib import Path

# srcディレクトリをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def test_text_proofreader():
    """CLI版テキスト校正機能のテスト"""
    try:
        from text_proofreader.main import TextProofreader
        
        # テストファイルのパス
        test_file = project_root / 'tests' / 'sample_document.txt'
        
        if not test_file.exists():
            print(f"テストファイルが見つかりません: {test_file}")
            return False
        
        # 校正アプリケーションを初期化
        proofreader = TextProofreader()
        
        print(f"テストファイルを校正中: {test_file}")
        print("=" * 50)
        
        # 校正実行
        result = proofreader.check_file(str(test_file))
        
        if result['success']:
            errors = result['errors']
            print(f"校正完了: {len(errors)} 件の問題を検出")
            
            # エラータイプ別統計
            error_types = {}
            for error in errors:
                error_type = error.get('type', 'unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            print("\nエラータイプ別統計:")
            for error_type, count in error_types.items():
                print(f"  {error_type}: {count} 件")
            
            # 最初の5件の詳細表示
            print("\n検出されたエラー例（最初の5件）:")
            for i, error in enumerate(errors[:5], 1):
                print(f"  {i}. 行{error.get('line', 0)}: "
                      f'"{error.get("original", "")}" → '
                      f'"{error.get("correction", error.get("suggestion", ""))}" '
                      f'({error.get("description", "")})')
            
            if len(errors) > 5:
                print(f"  ... 他 {len(errors) - 5} 件")
            
            print("\n>> CLI版テキスト校正機能は正常に動作しています。")
            return True
        else:
            print(f">> 校正処理に失敗: {result.get('error', 'unknown error')}")
            return False
            
    except ImportError as e:
        print(f">> モジュールのインポートエラー: {e}")
        print("必要なライブラリをインストールしてください:")
        print("pip install pandas openpyxl chardet")
        return False
    except Exception as e:
        print(f">> テスト実行エラー: {e}")
        return False

def main():
    """メイン関数"""
    print("CLI版テキスト校正アプリケーション テスト")
    print("=" * 50)
    
    success = test_text_proofreader()
    
    if success:
        print("\n>> テストが正常に完了しました!")
        print("\nWeb版を起動するには以下のコマンドを実行してください:")
        print("python run_web_app.py")
    else:
        print("\n>> テストで問題が発生しました。")
        print("エラーメッセージを確認して必要なライブラリをインストールしてください。")

if __name__ == "__main__":
    main()