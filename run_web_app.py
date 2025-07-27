from flask import Flask, request, render_template
from docx import Document
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file and file.filename.endswith('.docx'):
        document = Document(file)
        full_text = '\n'.join([p.text for p in document.paragraphs])
        return render_template('index.html', content=full_text)
    return '対応していないファイル形式です', 400

if __name__ == '__main__':
    app.run(debug=True)
