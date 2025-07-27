#!/usr/bin/env python3
import os
import sys
from pathlib import Path
import uvicorn

# srcディレクトリをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

# FastAPIアプリを読み込み
from web_proofreader.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
