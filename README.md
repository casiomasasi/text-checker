# テキスト校正アプリケーション

## 概要
テキストファイルを読み込み、誤字脱字、不適切な表現、文脈の不整合を自動検出・指摘するPythonアプリケーションです。

## テキスト校正アプリケーション

文章中の誤字脱字、不整合などを検出するアプリケーションです。  
FastAPI + Python で構成され、Web上から文章を送信すると簡易校正が受けられます。

## 機能
- **誤字脱字チェック**: ひらがな・カタカナの誤用、漢字変換ミス、タイプミス、送り仮名の誤りを検出
- **不適切表現チェック**: 差別的表現、敬語の誤用、口語表現、冗長表現を検出
- **文脈整合性チェック**: 代名詞の指示対象、時制の不整合、論理的矛盾、文章構造の問題を検出
- **多様な形式対応**: .txt, .md, .csv ファイルに対応
- **詳細レポート**: Excel形式で校正結果を出力、統計情報と修正提案を提供

## プロジェクト構造
```
.
├── src/
│   ├── text_proofreader/
│   │   ├── __init__.py
│   │   ├── main.py           # メインアプリケーション
│   │   ├── reader.py         # ファイル読み込み
│   │   ├── reporter.py       # レポート生成
│   │   ├── checkers/         # 校正チェッカー
│   │   │   ├── typo_checker.py      # 誤字脱字チェック
│   │   │   ├── expression_checker.py # 不適切表現チェック
│   │   │   └── context_checker.py   # 文脈整合性チェック
│   │   └── rules/           # 校正ルール定義
│   │       ├── typo_rules.json
│   │       ├── expression_rules.json
│   │       └── context_rules.json
│   └── main.py              # 旧メインスクリプト
├── tests/
│   ├── sample_text.txt      # テスト用サンプルテキスト
│   └── test_proofreader.py  # テストスクリプト
├── data/                    # 出力データ用（Git無視）
├── docs/
│   ├── requirements.md      # 要件定義
│   └── text_proofreading_requirements.md # 校正アプリ詳細仕様
├── .env.example            # 環境変数のテンプレート
├── .gitignore             # Git無視設定
└── README.md              # このファイル
```

## セットアップ方法

### 1. Poetryのセットアップ
```bash
# Poetryで依存関係をインストール
poetry install --no-root

# 仮想環境をアクティベート
poetry shell
```

### 2. 環境変数の設定
```bash
# .env.exampleをコピー
cp .env.example .env

# .envファイルを編集してAPIキーを設定
# API_KEY=your_actual_api_key_here
```

**⚠️ 重要: APIキーをコミットしないでください**
- `.env`ファイルは`.gitignore`に含まれています
- APIキーなどの機密情報は絶対にリポジトリにコミットしないでください
- `.env.example`はテンプレートとして使用し、実際の値は含めないでください

### 3. 実行方法

#### 基本的な使用方法
```bash
# テキストファイルを校正
python src/text_proofreader/main.py tests/sample_text.txt

# または poetry を使用
poetry run python src/text_proofreader/main.py tests/sample_text.txt
```

#### オプション付きの実行
```bash
# 出力ファイルを指定
python src/text_proofreader/main.py tests/sample_text.txt -o my_report.xlsx

# 特定のチェックを無効化
python src/text_proofreader/main.py tests/sample_text.txt --no-context --no-expressions

# CSVファイルの特定列を校正
python src/text_proofreader/main.py data.csv --csv-column text_column

# ファイル情報のみ表示
python src/text_proofreader/main.py tests/sample_text.txt --info-only
```

#### テストの実行
```bash
# アプリケーションのテスト
python tests/test_proofreader.py
```

## Excel出力時の注意事項（Noto Sans JP フォント）

### フォント設定
- 日本語文字を正しく表示するために、システムにNoto Sans JPフォントがインストールされていることを確認してください
- Windowsの場合：設定 > 個人用設定 > フォント からNoto Sans JPをインストール
- macOSの場合：Font Book.appでNoto Sans JPを追加
- Linuxの場合：パッケージマネージャーでnoto-fonts-cjkをインストール

### Excelでの日本語表示
- 生成されたExcelファイルで日本語が正しく表示されない場合は、Excelの設定でフォントをNoto Sans JPに変更してください
- セル範囲を選択 > 右クリック > セルの書式設定 > フォント > Noto Sans JP

### プログラムでのフォント指定
```python
# pandas ExcelWriterでフォントを指定する例
with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:
    df.to_excel(writer, sheet_name='Sheet1', index=False)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']
    
    # フォント形式を定義
    font_format = workbook.add_format({'font_name': 'Noto Sans JP'})
    worksheet.set_column('A:Z', None, font_format)
```

## 依存関係
- **pandas**: データ処理とExcel出力
- **openpyxl**: Excelファイル操作
- **chardet**: 文字エンコーディング自動判定
- **python-dotenv**: 環境変数の読み込み

## 校正機能の詳細

### 誤字脱字チェック
- ひらがな・カタカナの誤用（「わ」と「は」、「ずつ」と「づつ」など）
- 漢字変換ミス（「記録」と「記憶」、「以外」と「意外」など）
- タイプミス（重複文字、隣接キー誤入力）
- 送り仮名の誤り（「行う」と「行なう」など）

### 不適切表現チェック
- 差別的表現の検出
- 二重敬語や過度な敬語の指摘
- ビジネス文書での口語表現チェック
- 冗長表現の簡略化提案

### 文脈整合性チェック
- 代名詞の指示対象の曖昧性
- 文章内での時制の不整合
- 論理的飛躍や矛盾の検出
- 文体の統一性（敬語と常体の混在など）

### レポート機能
- **Excel形式**: 複数シートで詳細な分析結果を提供
- **統計情報**: エラー種別ごとの集計と評価スコア
- **色分け表示**: 重要度に応じた視覚的な表示
- **修正提案**: 具体的な改善案を提示

## Webアプリケーションの使用方法

### 起動方法
```bash
# Webアプリケーションを起動
python run_web_app.py

# または直接Flaskアプリを起動
cd src/web_proofreader
python app.py
```

### アクセス方法
1. ブラウザで http://localhost:5000 にアクセス
2. Wordファイル(.docx)をドラッグ&ドロップまたは選択してアップロード
3. 校正処理の完了を待つ
4. Googleドキュメント風エディタで結果を確認
5. コメントをクリックまたはキーボード操作で修正を適用
6. 完了後、修正済みファイルをダウンロード

### キーボード操作
- **↑↓キー**: コメント間移動
- **Enterキー**: コメントの修正を適用
- **Escキー**: コメントを無視
- **Tabキー**: フォーカス要素間移動
- **F1キー**: ヘルプ表示
- **Ctrl+S**: 文書保存
- **Ctrl+D**: ダウンロード

### 対応ファイル形式
- .docx (推奨)
- .doc (限定サポート)
- 最大ファイルサイズ: 10MB

## トラブルシューティング

### 基本的な問題
- APIキーが読み込まれない場合は、.envファイルの存在と内容を確認してください
- Excel出力でエラーが発生する場合は、dataディレクトリの書き込み権限を確認してください
- 日本語が文字化けする場合は、上記のフォント設定を確認してください

### Webアプリケーション関連
- **ファイルアップロードに失敗する場合**: ファイル形式(.docx)とサイズ(10MB以下)を確認
- **校正処理が完了しない場合**: ブラウザのコンソールでエラーを確認、ページを再読み込み
- **コメントが表示されない場合**: JavaScriptが有効になっているか確認
- **キーボード操作が効かない場合**: ページにフォーカスがあることを確認

### エラーメッセージと対処法
- 「ファイルが破損している」: 正しい.docxファイルか確認
- 「セッションが見つかりません」: ページを再読み込みして最初からやり直し
- 「処理がタイムアウトしました」: ファイルサイズを小さくするか、しばらく待ってから再試行