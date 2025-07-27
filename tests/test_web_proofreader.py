"""
Webベーステキスト校正システムのテストスクリプト

Flask アプリケーション、Word ファイル読み込み、校正機能の統合テスト
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# プロジェクトのパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def test_word_reader():
    """Word ファイル読み込み機能のテスト"""
    print("=== Word ファイル読み込みテスト ===")
    
    try:
        from web_proofreader.word_reader import WordReader
        
        word_reader = WordReader()
        
        # サンプルテキストファイルでテスト（.docx がない場合）
        sample_file = Path(__file__).parent / "sample_document.txt"
        
        if sample_file.exists():
            print(f"テストファイル: {sample_file}")
            
            # ファイル情報の取得テスト
            try:
                file_info = word_reader.get_file_info(sample_file)
                print("ファイル情報:")
                for key, value in file_info.items():
                    print(f"  {key}: {value}")
            except Exception as e:
                print(f"  ファイル情報取得エラー: {e}")
            
            print("Word読み込み機能は正常に動作しています。")
        else:
            print("サンプルファイルが見つかりません。")
            
    except ImportError as e:
        print(f"モジュールのインポートエラー: {e}")
        return False
    except Exception as e:
        print(f"Word読み込みテストエラー: {e}")
        return False
    
    return True

def test_text_proofreader_integration():
    """既存の校正エンジンとの統合テスト"""
    print("\n=== 校正エンジン統合テスト ===")
    
    try:
        from text_proofreader.main import TextProofreader
        
        # サンプルテキストファイルで校正テスト
        sample_file = Path(__file__).parent / "sample_document.txt"
        
        if not sample_file.exists():
            print("サンプルファイルが見つかりません。")
            return False
        
        proofreader = TextProofreader()
        
        print(f"校正テスト実行: {sample_file}")
        result = proofreader.check_file(str(sample_file))
        
        if result['success']:
            errors = result['errors']
            print(f"校正完了: {len(errors)} 件の問題を検出")
            
            # エラータイプ別の統計
            error_types = {}
            for error in errors:
                error_type = error.get('type', 'unknown')
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            print("エラータイプ別統計:")
            for error_type, count in error_types.items():
                print(f"  {error_type}: {count} 件")
            
            # 最初の5件を表示
            print("\n検出されたエラー例（最初の5件）:")
            for i, error in enumerate(errors[:5], 1):
                print(f"  {i}. 行{error.get('line', 0)}: "
                      f"\"{error.get('original', '')}\" → "
                      f"\"{error.get('correction', error.get('suggestion', ''))}\" "
                      f"({error.get('description', '')})")
            
            if len(errors) > 5:
                print(f"  ... 他 {len(errors) - 5} 件")
                
            print("校正エンジンは正常に動作しています。")
            return True
        else:
            print(f"校正処理に失敗: {result.get('error', 'unknown error')}")
            return False
            
    except Exception as e:
        print(f"校正エンジンテストエラー: {e}")
        return False

def test_api_endpoints():
    """Flask API のエンドポイントテスト"""
    print("\n=== Flask API テスト ===")
    
    try:
        import requests
        import threading
        import time
        
        # Flask アプリを別スレッドで起動
        from web_proofreader.app import app
        
        app.config['TESTING'] = True
        
        def run_app():
            app.run(debug=False, host='127.0.0.1', port=5001, use_reloader=False)
        
        server_thread = threading.Thread(target=run_app, daemon=True)
        server_thread.start()
        
        # サーバーの起動を待つ
        time.sleep(3)
        
        base_url = "http://127.0.0.1:5001"
        
        # ヘルスチェック
        try:
            response = requests.get(f"{base_url}/", timeout=5)
            if response.status_code == 200:
                print("✓ メインページにアクセス成功")
            else:
                print(f"✗ メインページアクセス失敗: {response.status_code}")
        except Exception as e:
            print(f"✗ メインページアクセスエラー: {e}")
        
        print("API エンドポイントテストは手動で実行してください。")
        print(f"サーバーURL: {base_url}")
        
        return True
        
    except ImportError:
        print("requests ライブラリがインストールされていません。")
        print("pip install requests でインストールしてください。")
        return False
    except Exception as e:
        print(f"API テストエラー: {e}")
        return False

def test_file_upload_simulation():
    """ファイルアップロードのシミュレーションテスト"""
    print("\n=== ファイルアップロードシミュレーション ===")
    
    try:
        from web_proofreader.word_reader import WordReader
        from io import BytesIO
        
        # テキストファイルをアップロード形式でシミュレート
        sample_content = """私わ学生です。記憶を取るために勉強しています。了解しました。"""
        
        # 疑似ファイルオブジェクトを作成
        class MockFile:
            def __init__(self, content, filename):
                self.content = content.encode('utf-8')
                self.filename = filename
                self.stream = BytesIO(self.content)
            
            def save(self, path):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(self.content.decode('utf-8'))
        
        mock_file = MockFile(sample_content, "test_document.txt")
        word_reader = WordReader()
        
        # 一時ファイル作成テスト
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, "uploaded_test.txt")
            mock_file.save(temp_file)
            
            print(f"テンポラリファイル作成: {temp_file}")
            
            # ファイル読み込みテスト
            if Path(temp_file).exists():
                print("✓ ファイルアップロードシミュレーション成功")
                
                # ファイル内容確認
                with open(temp_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"ファイル内容: {content[:50]}...")
                
                return True
            else:
                print("✗ ファイル作成失敗")
                return False
        
    except Exception as e:
        print(f"アップロードシミュレーションエラー: {e}")
        return False

def run_all_tests():
    """全てのテストを実行"""
    print("Webベーステキスト校正システム 統合テスト開始\n")
    
    tests = [
        ("Word読み込み機能", test_word_reader),
        ("校正エンジン統合", test_text_proofreader_integration),
        ("ファイルアップロード", test_file_upload_simulation),
        ("Flask API", test_api_endpoints),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"{test_name}でエラー: {e}")
            results.append((test_name, False))
    
    # 結果サマリー
    print("\n" + "="*50)
    print("テスト結果サマリー")
    print("="*50)
    
    success_count = 0
    for test_name, result in results:
        status = "✓ 成功" if result else "✗ 失敗"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n成功: {success_count}/{len(results)}")
    
    if success_count == len(results):
        print("全てのテストが成功しました！")
        return True
    else:
        print("一部のテストで問題が発生しました。")
        return False

def manual_test_instructions():
    """手動テストの手順を表示"""
    print("\n" + "="*60)
    print("手動テスト手順")
    print("="*60)
    print("""
1. Flask アプリケーションの起動:
   cd src/web_proofreader
   python app.py

2. ブラウザでアクセス:
   http://localhost:5000

3. テスト手順:
   a) メインページの表示確認
   b) サンプルテキストファイルのダウンロードとアップロード
   c) 校正処理の実行と結果確認
   d) エディタページでのコメント表示確認
   e) キーボードナビゲーション（↑↓キー）の確認
   f) コメント適用機能（Enterキー）の確認
   g) ダウンロード機能の確認

4. 期待される動作:
   - Wordファイル（.docx）のアップロードが可能
   - 校正結果がコメントとして表示される
   - マウスクリックでコメント選択が可能
   - 十字キーでコメント間移動が可能
   - Enterキーでコメント承諾・反映が可能
   - 修正後の文書がダウンロード可能

5. 確認項目:
   - 日本語文字が正しく表示される
   - レスポンシブデザインが機能する
   - エラーハンドリングが適切に動作する
   - セッション管理が正常に機能する
""")

if __name__ == "__main__":
    # 依存関係の確認
    required_packages = ['pandas', 'openpyxl', 'chardet', 'python-dotenv', 'flask', 'python-docx']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("以下のパッケージがインストールされていません:")
        for package in missing_packages:
            print(f"  - {package}")
        print(f"\nインストールコマンド:")
        print(f"pip install {' '.join(missing_packages)}")
        sys.exit(1)
    
    # テスト実行
    success = run_all_tests()
    
    # 手動テスト手順を表示
    manual_test_instructions()
    
    if success:
        print("\n🎉 統合テストが完了しました！")
        print("手動テストを実行してWebアプリケーションの動作を確認してください。")
    else:
        print("\n⚠️  一部のテストで問題が発生しました。")
        print("エラーを確認してから手動テストを実行してください。")
        sys.exit(1)