/* ファイルアップロード機能 */

class FileUploader {
    constructor() {
        this.dropzone = document.getElementById('dropzone');
        this.fileInput = document.getElementById('fileInput');
        this.progressContainer = document.getElementById('uploadProgress');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.allowedTypes = ['.docx', '.doc'];
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDropzone();
    }

    setupEventListeners() {
        // ファイル入力の変更
        this.fileInput.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                this.handleFile(file);
            }
        });

        // ドラッグ&ドロップ
        this.dropzone.addEventListener('click', () => {
            this.fileInput.click();
        });
    }

    setupDropzone() {
        // ドラッグオーバー
        this.dropzone.addEventListener('dragover', (event) => {
            event.preventDefault();
            this.dropzone.classList.add('dragover');
        });

        // ドラッグリーブ
        this.dropzone.addEventListener('dragleave', (event) => {
            event.preventDefault();
            if (!this.dropzone.contains(event.relatedTarget)) {
                this.dropzone.classList.remove('dragover');
            }
        });

        // ドロップ
        this.dropzone.addEventListener('drop', (event) => {
            event.preventDefault();
            this.dropzone.classList.remove('dragover');
            
            const files = event.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });
    }

    validateFile(file) {
        const errors = [];

        // ファイル名チェック
        if (!file.name) {
            errors.push('ファイル名が無効です。');
        }

        // ファイルサイズチェック
        if (file.size > this.maxFileSize) {
            errors.push(`ファイルサイズが大きすぎます。上限: ${Utils.formatFileSize(this.maxFileSize)}`);
        }

        // ファイル形式チェック
        const extension = '.' + file.name.split('.').pop().toLowerCase();
        if (!this.allowedTypes.includes(extension)) {
            errors.push(`サポートされていないファイル形式です。対応形式: ${this.allowedTypes.join(', ')}`);
        }

        // 空ファイルチェック
        if (file.size === 0) {
            errors.push('ファイルが空です。');
        }

        return errors;
    }

    async handleFile(file) {
        // バリデーション
        const validationErrors = this.validateFile(file);
        if (validationErrors.length > 0) {
            Utils.showError(validationErrors.join(' '));
            return;
        }

        try {
            // UI更新
            this.showProgress();
            Utils.hideMessage('errorMessage');
            Utils.hideMessage('successMessage');

            // プログレス更新
            this.updateProgress(10, 'ファイルを準備中...');

            // FormDataを作成
            const formData = new FormData();
            formData.append('file', file);

            // プログレス更新
            this.updateProgress(30, 'アップロード中...');

            // XMLHttpRequestを使用してプログレスを追跡
            const response = await this.uploadWithProgress(formData);

            // プログレス更新
            this.updateProgress(90, '処理中...');

            // レスポンス処理
            if (response.session_id) {
                this.updateProgress(100, 'アップロード完了!');
                
                // 成功メッセージ表示
                Utils.showSuccess('ファイルアップロードが完了しました。校正処理を開始しています...');
                
                // セッション情報を保存
                SessionManager.save({
                    sessionId: response.session_id,
                    fileName: file.name,
                    fileSize: file.size
                });

                // 校正処理の監視を開始
                setTimeout(() => {
                    this.monitorProcessing(response.session_id);
                }, 1000);

            } else {
                throw new Error('サーバーからの応答が不正です。');
            }

        } catch (error) {
            console.error('Upload error:', error);
            Utils.showError(error.message || 'アップロードに失敗しました。');
            this.hideProgress();
        }
    }

    uploadWithProgress(formData) {
        return new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();

            // プログレス監視
            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percentComplete = (event.loaded / event.total) * 60 + 30; // 30-90%
                    this.updateProgress(percentComplete, 'アップロード中...');
                }
            });

            // 完了時
            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        resolve(response);
                    } catch (error) {
                        reject(new Error('サーバーからの応答を解析できませんでした。'));
                    }
                } else {
                    try {
                        const errorResponse = JSON.parse(xhr.responseText);
                        reject(new Error(errorResponse.error || `HTTP ${xhr.status} エラー`));
                    } catch (error) {
                        reject(new Error(`HTTP ${xhr.status} エラーが発生しました。`));
                    }
                }
            });

            // エラー時
            xhr.addEventListener('error', () => {
                reject(new Error('ネットワークエラーが発生しました。'));
            });

            // タイムアウト時
            xhr.addEventListener('timeout', () => {
                reject(new Error('アップロードがタイムアウトしました。'));
            });

            // リクエスト送信
            xhr.timeout = 60000; // 60秒
            xhr.open('POST', '/api/upload');
            xhr.send(formData);
        });
    }

    async monitorProcessing(sessionId) {
        const maxAttempts = 60; // 最大5分間監視
        let attempts = 0;

        const checkStatus = async () => {
            try {
                attempts++;
                const response = await Utils.apiRequest(`/api/status/${sessionId}`);

                switch (response.status) {
                    case 'processing':
                        this.updateProgress(95, '校正処理中...');
                        if (attempts < maxAttempts) {
                            setTimeout(checkStatus, 5000); // 5秒後に再チェック
                        } else {
                            throw new Error('処理がタイムアウトしました。');
                        }
                        break;

                    case 'completed':
                        this.updateProgress(100, '処理完了!');
                        Utils.showSuccess('校正処理が完了しました。エディタページに移動します...');
                        
                        setTimeout(() => {
                            window.location.href = `/editor/${sessionId}`;
                        }, 2000);
                        break;

                    case 'error':
                        throw new Error(response.error_message || '校正処理中にエラーが発生しました。');

                    default:
                        if (attempts < maxAttempts) {
                            setTimeout(checkStatus, 5000);
                        } else {
                            throw new Error('処理状況を確認できませんでした。');
                        }
                }

            } catch (error) {
                console.error('Status check error:', error);
                Utils.showError(error.message);
                this.hideProgress();
            }
        };

        // 最初のチェックを開始
        setTimeout(checkStatus, 2000);
    }

    showProgress() {
        this.progressContainer.classList.remove('d-none');
        this.dropzone.style.opacity = '0.5';
        this.dropzone.style.pointerEvents = 'none';
    }

    hideProgress() {
        this.progressContainer.classList.add('d-none');
        this.dropzone.style.opacity = '1';
        this.dropzone.style.pointerEvents = 'auto';
        this.updateProgress(0, '');
    }

    updateProgress(percentage, text) {
        this.progressBar.style.width = `${percentage}%`;
        this.progressBar.setAttribute('aria-valuenow', percentage);
        this.progressText.textContent = text;
    }
}

// ページ読み込み時に初期化
document.addEventListener('DOMContentLoaded', function() {
    // 既存セッションチェック
    const existingSession = SessionManager.load();
    if (existingSession && existingSession.sessionId) {
        const shouldResume = confirm(
            `前回のセッション（${existingSession.fileName}）が見つかりました。\\n` +
            '続きから開始しますか？'
        );
        
        if (shouldResume) {
            // セッション状況を確認
            Utils.apiRequest(`/api/status/${existingSession.sessionId}`)
                .then(response => {
                    if (response.status === 'completed') {
                        window.location.href = `/editor/${existingSession.sessionId}`;
                    } else {
                        SessionManager.clear();
                        new FileUploader();
                    }
                })
                .catch(error => {
                    console.error('Session check failed:', error);
                    SessionManager.clear();
                    new FileUploader();
                });
        } else {
            SessionManager.clear();
            new FileUploader();
        }
    } else {
        new FileUploader();
    }
});

// ページ離脱時の警告（アップロード中のみ）
window.addEventListener('beforeunload', function(event) {
    const progressContainer = document.getElementById('uploadProgress');
    if (progressContainer && !progressContainer.classList.contains('d-none')) {
        event.preventDefault();
        event.returnValue = 'アップロード処理中です。ページを離れますか？';
        return event.returnValue;
    }
});

// エラー処理の強化
window.addEventListener('error', function(event) {
    if (event.filename && event.filename.includes('upload.js')) {
        Utils.showError('アップロード処理でエラーが発生しました。ページを再読み込みしてください。');
    }
});

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FileUploader;
} else {
    window.FileUploader = FileUploader;
}