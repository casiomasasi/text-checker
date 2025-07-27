/* エディタ機能 */

class TextEditor {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.currentText = '';
        this.originalText = '';
        this.metadata = {};
        this.isLoaded = false;
        
        // DOM要素
        this.textEditor = document.getElementById('textEditor');
        this.fileName = document.getElementById('fileName');
        this.fileStats = document.getElementById('fileStats');
        
        this.init();
    }

    async init() {
        try {
            await this.loadDocument();
            this.setupEventListeners();
            this.isLoaded = true;
        } catch (error) {
            console.error('Editor initialization failed:', error);
            Utils.showError('エディタの初期化に失敗しました。');
        }
    }

    async loadDocument() {
        try {
            Utils.setLoading(true, '文書を読み込み中...');
            
            const response = await Utils.apiRequest(`/api/document/${this.sessionId}`);
            
            this.originalText = response.original_text;
            this.currentText = response.current_text;
            this.metadata = response.metadata;
            
            // UI更新
            this.updateFileInfo();
            this.renderText();
            
            Utils.setLoading(false);
        } catch (error) {
            Utils.setLoading(false);
            throw error;
        }
    }

    updateFileInfo() {
        this.fileName.textContent = this.metadata.file_name || 'Unknown File';
        this.fileStats.textContent = 
            `${this.metadata.char_count || 0}文字 / ${comments.length || 0}コメント`;
    }

    renderText() {
        if (!this.currentText) {
            this.textEditor.innerHTML = '<p class="text-muted">テキストが見つかりませんでした。</p>';
            return;
        }

        // テキストをレンダリング
        this.textEditor.innerHTML = '';
        
        // 段落ごとに分割
        const paragraphs = this.currentText.split('\n\n');
        let currentPosition = 0;
        
        paragraphs.forEach((paragraph, index) => {
            if (paragraph.trim()) {
                const p = document.createElement('p');
                p.style.marginBottom = '1rem';
                p.style.lineHeight = '1.8';
                
                // コメントハイライトを適用
                const highlightedText = this.applyHighlights(paragraph, currentPosition);
                p.innerHTML = highlightedText;
                
                this.textEditor.appendChild(p);
                currentPosition += paragraph.length + 2; // \n\n分を追加
            }
        });

        // エディタを編集可能に設定
        this.textEditor.contentEditable = true;
        this.textEditor.setAttribute('tabindex', '0');
    }

    applyHighlights(text, basePosition) {
        if (!comments || comments.length === 0) {
            return Utils.escapeHtml(text);
        }

        let result = text;
        const highlights = [];

        // この段落に関連するコメントを取得
        comments.forEach(comment => {
            if (comment.applied) return;

            const commentStart = comment.position.start - basePosition;
            const commentEnd = comment.position.end - basePosition;

            // この段落内にあるコメントのみ処理
            if (commentStart >= 0 && commentStart < text.length) {
                highlights.push({
                    start: commentStart,
                    end: Math.min(commentEnd - basePosition, text.length),
                    comment: comment
                });
            }
        });

        // 位置でソート（後ろから処理するため逆順）
        highlights.sort((a, b) => b.start - a.start);

        // ハイライトを適用
        highlights.forEach(highlight => {
            const { start, end, comment } = highlight;
            const originalText = result.substring(start, end);
            const highlightedText = 
                `<span class="text-highlight severity-${comment.severity}" 
                       data-comment-id="${comment.id}"
                       title="${Utils.escapeHtml(comment.description)}"
                       onclick="selectComment('${comment.id}')"
                       tabindex="0">
                    ${Utils.escapeHtml(originalText)}
                </span>`;
            
            result = result.substring(0, start) + highlightedText + result.substring(end);
        });

        return result;
    }

    updateText(newText) {
        this.currentText = newText;
        this.renderText();
        this.updateFileInfo();
        
        // コメント位置を更新
        if (window.commentsManager) {
            window.commentsManager.updateDisplay();
        }
    }

    setupEventListeners() {
        // テキスト変更の監視
        this.textEditor.addEventListener('input', Utils.debounce(() => {
            this.handleTextChange();
        }, 500));

        // フォーカス管理
        this.textEditor.addEventListener('focus', () => {
            this.textEditor.classList.add('focused');
        });

        this.textEditor.addEventListener('blur', () => {
            this.textEditor.classList.remove('focused');
        });

        // キーボードイベント
        this.textEditor.addEventListener('keydown', (event) => {
            this.handleKeyDown(event);
        });
    }

    handleTextChange() {
        // 手動編集による変更を検出
        const newText = this.textEditor.textContent || '';
        
        if (newText !== this.currentText) {
            this.currentText = newText;
            
            // 変更をマーク
            this.markAsModified();
            
            // 統計更新
            this.updateFileInfo();
        }
    }

    handleKeyDown(event) {
        // Ctrl+Z: 元に戻す
        if (event.ctrlKey && event.key === 'z') {
            event.preventDefault();
            this.undo();
        }
        
        // Ctrl+Y: やり直し
        if (event.ctrlKey && event.key === 'y') {
            event.preventDefault();
            this.redo();
        }
        
        // Ctrl+S: 保存
        if (event.ctrlKey && event.key === 's') {
            event.preventDefault();
            this.save();
        }

        // Ctrl+D: ダウンロード
        if (event.ctrlKey && event.key === 'd') {
            event.preventDefault();
            downloadDocument();
        }
    }

    markAsModified() {
        // 未保存の変更があることを表示
        if (!this.fileName.textContent.includes('*')) {
            this.fileName.textContent += ' *';
        }
    }

    clearModified() {
        // 保存済みマークをクリア
        this.fileName.textContent = this.fileName.textContent.replace(' *', '');
    }

    async save() {
        try {
            Utils.setLoading(true, '保存中...');
            
            // 現在のテキスト状態を保存
            // 実際の実装では、APIにテキストを送信して保存
            
            NotificationManager.show('文書が保存されました', 'success');
            this.clearModified();
            
            Utils.setLoading(false);
        } catch (error) {
            Utils.setLoading(false);
            Utils.showError('保存に失敗しました: ' + error.message);
        }
    }

    undo() {
        // ブラウザの標準Undo機能を使用
        document.execCommand('undo');
        this.handleTextChange();
    }

    redo() {
        // ブラウザの標準Redo機能を使用
        document.execCommand('redo');
        this.handleTextChange();
    }

    // ハイライト要素を取得
    getHighlightElements() {
        return this.textEditor.querySelectorAll('.text-highlight');
    }

    // 特定のコメントをハイライト
    highlightComment(commentId) {
        // 既存のアクティブハイライトを削除
        this.getHighlightElements().forEach(el => {
            el.classList.remove('active');
        });

        // 対象のコメントをハイライト
        const targetElement = this.textEditor.querySelector(`[data-comment-id="${commentId}"]`);
        if (targetElement) {
            targetElement.classList.add('active');
            
            // 要素をビューポートに表示
            targetElement.scrollIntoView({
                behavior: 'smooth',
                block: 'center'
            });
            
            return targetElement;
        }
        
        return null;
    }

    // ハイライトをクリア
    clearHighlights() {
        this.getHighlightElements().forEach(el => {
            el.classList.remove('active');
        });
    }

    // テキスト置換（コメント適用時）
    replaceText(startPos, endPos, newText) {
        try {
            // 現在のテキストから該当部分を置換
            const beforeText = this.currentText.substring(0, startPos);
            const afterText = this.currentText.substring(endPos);
            
            this.currentText = beforeText + newText + afterText;
            
            // 表示を更新
            this.renderText();
            
            // 変更をマーク
            this.markAsModified();
            
            // 成功を示すアニメーション
            const replacedElement = this.textEditor.querySelector(`[data-comment-id]:not(.applied)`);
            if (replacedElement) {
                Utils.animateElement(replacedElement, 'pulse');
            }
            
            return true;
        } catch (error) {
            console.error('Text replacement failed:', error);
            return false;
        }
    }

    // エディタの状態を取得
    getState() {
        return {
            currentText: this.currentText,
            originalText: this.originalText,
            metadata: this.metadata,
            isModified: this.fileName.textContent.includes('*'),
            isLoaded: this.isLoaded
        };
    }

    // フォーカスを設定
    focus() {
        this.textEditor.focus();
    }

    // 選択範囲を取得
    getSelection() {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            return {
                startOffset: range.startOffset,
                endOffset: range.endOffset,
                selectedText: selection.toString()
            };
        }
        return null;
    }
}

// グローバル変数
let textEditor = null;

// エディタを初期化
async function initializeEditor(sessionId) {
    try {
        textEditor = new TextEditor(sessionId);
        return textEditor;
    } catch (error) {
        console.error('Failed to initialize editor:', error);
        Utils.showError('エディタの初期化に失敗しました。');
        return null;
    }
}

// 文書を読み込み
async function loadDocument() {
    if (!sessionId) {
        Utils.showError('セッションIDが見つかりません。');
        return;
    }

    try {
        // エディタを初期化
        await initializeEditor(sessionId);
        
        // コメント管理システムを初期化
        if (window.CommentsManager) {
            window.commentsManager = new window.CommentsManager(sessionId);
            await window.commentsManager.loadComments();
        }
        
    } catch (error) {
        console.error('Failed to load document:', error);
        Utils.showError('文書の読み込みに失敗しました。');
    }
}

// コメントを選択
function selectComment(commentId) {
    if (textEditor) {
        textEditor.highlightComment(commentId);
    }
    
    if (window.commentsManager) {
        window.commentsManager.selectComment(commentId);
    }
}

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TextEditor, initializeEditor, loadDocument, selectComment };
} else {
    window.TextEditor = TextEditor;
    window.initializeEditor = initializeEditor;
    window.loadDocument = loadDocument;
    window.selectComment = selectComment;
}