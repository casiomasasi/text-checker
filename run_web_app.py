from flask import Flask, render_template, request
import os

app = Flask(__name__)

def check_dependencies():
    """必要な依存関係をチェック"""
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

@app.route('/')
def index():
    return "テキスト校正Webアプリケーション起動中..."

if __name__ == '__main__':
    if check_dependencies():
        app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
