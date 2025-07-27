#!/usr/bin/env python3
"""
Webベーステキスト校正アプリケーション起動スクリプト

Flask アプリケーションを起動し、Webインターフェースを提供します。
"""

import os
import sys
from pathlib import Path

def check_dependencies():
    """必要な依存関係をチェック"""
    # パッケージ名 → import名 の対応辞書に変更
    required_packages = {
        'flask': 'flask',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
        'chardet': 'chardet',
        'python-dotenv': 'dotenv',
        'python-docx': 'docx'
    }
    
    missing_packages = []
    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(">> 以下のパッケージがインストールされていません:")
        for package in missing_packages:
            print(f"   - {package}")
        print(f"\n>> インストールコマンド:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True


def main():
    """メイン関数"""
    print(">> テキスト校正Webアプリケーション起動中...")
    
    # 依存関係チェック
    if not check_dependencies():
        print("\n>> 依存関係をインストールしてから再実行してください。")
        sys.exit(1)
    
    # srcディレクトリをパスに追加
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root / 'src'))
    
    try:
        # Flaskアプリを読み込み
        from web_proofreader.app import app
        
        # 環境変数から設定を取得
        host = os.environ.get("HOST", "127.0.0.1")
        port = int(os.environ.get("PORT", 5000))
        debug = os.environ.get("DEBUG", "False").lower() == "true"
        
        print(f">> サーバーを起動中: http://{host}:{port}")
        print(">> Ctrl+C で停止できます")
        
        # Flaskアプリケーション起動
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True
        )
        
    except ImportError as e:
        print(f">> モジュールのインポートエラー: {e}")
        print(">> src/web_proofreader/ ディレクトリが正しく配置されているか確認してください。")
        sys.exit(1)
    except Exception as e:
        print(f">> アプリケーション起動エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
