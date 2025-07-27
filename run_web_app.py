#!/usr/bin/env python3
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

def run_app():
    try:
        from web_proofreader.app import app

        port = int(os.environ.get("PORT", 5000))
        app.run(
            debug=True,
            host='0.0.0.0',
            port=port,
            use_reloader=True
        )

    except KeyboardInterrupt:
        print("\n\n>> サーバーを停止しました")
    except Exception as e:
        print(f"\n>> アプリケーション起動エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_app()
