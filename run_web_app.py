from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 必要ならCORS許可

@app.route('/')
def index():
    return render_template('index.html')  # 上記HTMLを templates/index.html に保存してください

@app.route('/suggest', methods=['POST'])
def suggest():
    data = request.get_json()
    text = data.get('text', '')

    # ダミー校正ロジック：本来はLLM連携など
    suggestions = []
    if '致します' in text:
        suggestions.append({
            "original": "致します",
            "suggestion": "いたします",
            "reason": "敬語のひらがな表記が推奨されます"
        })
    if '下さい' in text:
        suggestions.append({
            "original": "下さい",
            "suggestion": "ください",
            "reason": "漢字の敬語は避け、ひらがなが推奨されます"
        })

    return jsonify({"suggestions": suggestions})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)