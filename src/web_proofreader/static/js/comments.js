/* コメント管理機能 */

class CommentsManager {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.comments = [];
        this.selectedCommentId = null;
        this.filterMode = 'all'; // all, unapplied
        
        // DOM要素
        this.commentsList = document.getElementById('commentsList');
        this.noComments = document.getElementById('noComments');
        this.appliedCount = document.getElementById('appliedCount');
        this.totalCount = document.getElementById('totalCount');
        this.progressBar = document.getElementById('progressBar');
        this.applyAllBtn = document.getElementById('applyAllBtn');
        
        this.init();
    }

    async init() {
        this.setupEventListeners();
    }

    setupEventListeners() {
        // フィルターボタン
        document.getElementById('filterAll')?.addEventListener('click', () => {
            this.setFilter('all');
        });
        
        document.getElementById('filterUnapplied')?.addEventListener('click', () => {
            this.setFilter('unapplied');
        });
    }

    async loadComments() {
        try {
            const response = await Utils.apiRequest(`/api/comments/${this.sessionId}`);
            this.comments = response.comments || [];
            
            // グローバル変数としても設定（他のモジュールから参照用）
            window.comments = this.comments;
            
            this.updateDisplay();
            this.updateStatistics();
            
        } catch (error) {
            console.error('Failed to load comments:', error);
            Utils.showError('コメントの読み込みに失敗しました。');
        }
    }

    updateDisplay() {
        if (!this.commentsList) return;

        // フィルタリング
        const filteredComments = this.getFilteredComments();

        if (filteredComments.length === 0) {
            this.showNoComments();
            return;
        }

        this.hideNoComments();
        this.renderComments(filteredComments);
    }

    getFilteredComments() {
        switch (this.filterMode) {
            case 'unapplied':
                return this.comments.filter(c => !c.applied);
            case 'all':
            default:
                return this.comments;
        }
    }

    renderComments(commentsToShow) {
        const fragment = document.createDocumentFragment();

        commentsToShow.forEach((comment, index) => {
            const commentElement = this.createCommentElement(comment, index);
            fragment.appendChild(commentElement);
        });

        this.commentsList.innerHTML = '';
        this.commentsList.appendChild(fragment);
    }

    createCommentElement(comment, index) {
        const card = document.createElement('div');
        card.className = `comment-card ${comment.applied ? 'applied' : ''}`;
        card.setAttribute('data-comment-id', comment.id);
        card.setAttribute('tabindex', '0');

        const severityColor = this.getSeverityColor(comment.severity);
        const severityIcon = this.getSeverityIcon(comment.severity);

        card.innerHTML = `
            <div class="card-body p-3">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <div class="d-flex align-items-center">
                        <i class="${severityIcon} me-2" style="color: ${severityColor};"></i>
                        <span class="badge severity-badge severity-${comment.severity}">
                            ${comment.severity.toUpperCase()}
                        </span>
                    </div>
                    <small class="text-muted">${comment.line ? `行${comment.line}` : ''}</small>
                </div>
                
                <div class="mb-2">
                    <strong class="text-danger small">修正前:</strong>
                    <div class="bg-light p-2 rounded small">
                        <del>${Utils.escapeHtml(comment.original)}</del>
                    </div>
                </div>
                
                <div class="mb-2">
                    <strong class="text-success small">修正案:</strong>
                    <div class="bg-light p-2 rounded small">
                        <ins>${Utils.escapeHtml(comment.suggestion)}</ins>
                    </div>
                </div>
                
                <div class="mb-3">
                    <strong class="small">説明:</strong>
                    <p class="small text-muted mb-0">${Utils.escapeHtml(comment.description)}</p>
                </div>
                
                <div class="d-flex gap-2">
                    ${comment.applied ? 
                        '<span class="badge bg-success"><i class="fas fa-check me-1"></i>適用済み</span>' :
                        `<button class="btn btn-primary btn-sm apply-button" 
                                onclick="applyComment('${comment.id}')" 
                                title="この修正を適用 (Enter)">
                            <i class="fas fa-check me-1"></i>適用
                        </button>
                        <button class="btn btn-outline-secondary btn-sm" 
                                onclick="ignoreComment('${comment.id}')" 
                                title="この修正を無視 (Esc)">
                            <i class="fas fa-times me-1"></i>無視
                        </button>`
                    }
                </div>
            </div>
        `;

        // イベントリスナー
        card.addEventListener('click', () => {
            this.selectComment(comment.id);
        });

        card.addEventListener('keydown', (event) => {
            this.handleCommentKeyDown(event, comment.id);
        });

        return card;
    }

    getSeverityColor(severity) {
        const colors = {
            high: '#dc3545',
            medium: '#ffc107',
            low: '#0dcaf0'
        };
        return colors[severity] || colors.medium;
    }

    getSeverityIcon(severity) {
        const icons = {
            high: 'fas fa-exclamation-circle',
            medium: 'fas fa-exclamation-triangle',
            low: 'fas fa-info-circle'
        };
        return icons[severity] || icons.medium;
    }

    handleCommentKeyDown(event, commentId) {
        switch (event.key) {
            case 'Enter':
                event.preventDefault();
                this.applyComment(commentId);
                break;
            case 'Escape':
                event.preventDefault();
                this.ignoreComment(commentId);
                break;
            case 'ArrowUp':
                event.preventDefault();
                this.navigateComment(-1);
                break;
            case 'ArrowDown':
                event.preventDefault();
                this.navigateComment(1);
                break;
        }
    }

    selectComment(commentId) {
        // 既存の選択を解除
        this.clearSelection();

        // 新しい選択を設定
        this.selectedCommentId = commentId;

        // UI更新
        const commentElement = document.querySelector(`[data-comment-id="${commentId}"]`);
        if (commentElement) {
            commentElement.classList.add('active');
            commentElement.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }

        // エディタ内のハイライトも更新
        if (window.textEditor) {
            window.textEditor.highlightComment(commentId);
        }
    }

    clearSelection() {
        // コメントカードの選択を解除
        document.querySelectorAll('.comment-card.active').forEach(el => {
            el.classList.remove('active');
        });

        // エディタ内のハイライトも解除
        if (window.textEditor) {
            window.textEditor.clearHighlights();
        }

        this.selectedCommentId = null;
    }

    navigateComment(direction) {
        const visibleComments = this.getFilteredComments();
        if (visibleComments.length === 0) return;

        let currentIndex = -1;
        if (this.selectedCommentId) {
            currentIndex = visibleComments.findIndex(c => c.id === this.selectedCommentId);
        }

        let newIndex = currentIndex + direction;
        
        // 範囲チェック
        if (newIndex < 0) {
            newIndex = visibleComments.length - 1;
        } else if (newIndex >= visibleComments.length) {
            newIndex = 0;
        }

        const newComment = visibleComments[newIndex];
        if (newComment) {
            this.selectComment(newComment.id);
        }
    }

    async applyComment(commentId, showConfirmation = true) {
        const comment = this.comments.find(c => c.id === commentId);
        if (!comment) {
            Utils.showError('コメントが見つかりません。');
            return;
        }

        if (comment.applied) {
            NotificationManager.show('この修正は既に適用済みです。', 'warning');
            return;
        }

        // 確認ダイアログ（オプション）
        if (showConfirmation) {
            const shouldApply = await this.showConfirmationDialog(comment);
            if (!shouldApply) return;
        }

        try {
            Utils.setLoading(true, '修正を適用中...');

            const response = await Utils.apiRequest('/api/apply-fix', {
                method: 'POST',
                body: JSON.stringify({
                    session_id: this.sessionId,
                    comment_id: commentId
                })
            });

            if (response.success) {
                // コメントを適用済みに変更
                comment.applied = true;

                // UI更新
                this.updateDisplay();
                this.updateStatistics();

                // エディタのテキストを更新
                if (window.textEditor && response.current_text) {
                    window.textEditor.updateText(response.current_text);
                }

                NotificationManager.show('修正が適用されました。', 'success');

                // 次のコメントに移動
                this.navigateToNextUnapplied();

            } else {
                throw new Error(response.message || '修正の適用に失敗しました。');
            }

        } catch (error) {
            console.error('Apply comment failed:', error);
            Utils.showError(error.message);
        } finally {
            Utils.setLoading(false);
        }
    }

    async showConfirmationDialog(comment) {
        return new Promise((resolve) => {
            // モーダルに情報を設定
            document.getElementById('originalText').textContent = comment.original;
            document.getElementById('suggestionText').textContent = comment.suggestion;
            document.getElementById('descriptionText').textContent = comment.description;

            // モーダルを表示
            const modal = new bootstrap.Modal(document.getElementById('confirmModal'));
            modal.show();

            // 確認ボタンのクリックハンドラー
            const confirmButton = document.querySelector('#confirmModal .btn-primary');
            const newConfirmButton = confirmButton.cloneNode(true);
            confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);

            newConfirmButton.addEventListener('click', () => {
                modal.hide();
                resolve(true);
            });

            // モーダルが閉じられた時のハンドラー
            document.getElementById('confirmModal').addEventListener('hidden.bs.modal', () => {
                resolve(false);
            }, { once: true });
        });
    }

    ignoreComment(commentId) {
        const comment = this.comments.find(c => c.id === commentId);
        if (!comment) return;

        if (confirm(`「${comment.original}」の修正を無視しますか？`)) {
            // コメントを適用済みとして扱う（ただし実際には適用しない）
            comment.applied = true;
            comment.ignored = true;

            this.updateDisplay();
            this.updateStatistics();

            NotificationManager.show('修正を無視しました。', 'info');
            this.navigateToNextUnapplied();
        }
    }

    navigateToNextUnapplied() {
        const unappliedComments = this.comments.filter(c => !c.applied);
        if (unappliedComments.length > 0) {
            this.selectComment(unappliedComments[0].id);
        } else {
            this.clearSelection();
            NotificationManager.show('全ての修正が完了しました！', 'success');
        }
    }

    updateStatistics() {
        const appliedCount = this.comments.filter(c => c.applied).length;
        const totalCount = this.comments.length;

        if (this.appliedCount) {
            this.appliedCount.textContent = appliedCount;
        }
        
        if (this.totalCount) {
            this.totalCount.textContent = totalCount;
        }

        // プログレスバー更新
        if (this.progressBar) {
            const percentage = totalCount > 0 ? (appliedCount / totalCount) * 100 : 0;
            this.progressBar.style.width = `${percentage}%`;
        }

        // 全適用ボタンの状態更新
        if (this.applyAllBtn) {
            const unappliedCount = totalCount - appliedCount;
            this.applyAllBtn.disabled = unappliedCount === 0;
            this.applyAllBtn.textContent = unappliedCount > 0 ? 
                `全て適用 (${unappliedCount})` : '全て適用済み';
        }
    }

    setFilter(mode) {
        this.filterMode = mode;

        // ボタンの状態更新
        document.getElementById('filterAll')?.classList.toggle('active', mode === 'all');
        document.getElementById('filterUnapplied')?.classList.toggle('active', mode === 'unapplied');

        this.updateDisplay();
    }

    showNoComments() {
        if (this.commentsList) {
            this.commentsList.innerHTML = '';
        }
        if (this.noComments) {
            this.noComments.classList.remove('d-none');
        }
    }

    hideNoComments() {
        if (this.noComments) {
            this.noComments.classList.add('d-none');
        }
    }

    // 全コメント適用
    async applyAllComments() {
        const unappliedComments = this.comments.filter(c => !c.applied);
        
        if (unappliedComments.length === 0) {
            NotificationManager.show('適用可能なコメントがありません。', 'info');
            return;
        }

        const shouldApply = confirm(`${unappliedComments.length}件の修正を全て適用しますか？`);
        if (!shouldApply) return;

        Utils.setLoading(true, '全ての修正を適用中...');

        let successCount = 0;
        let errorCount = 0;

        for (const comment of unappliedComments) {
            try {
                await this.applyComment(comment.id, false); // 確認なしで適用
                successCount++;
            } catch (error) {
                console.error(`Failed to apply comment ${comment.id}:`, error);
                errorCount++;
            }
        }

        Utils.setLoading(false);

        if (errorCount === 0) {
            NotificationManager.show(`${successCount}件の修正を全て適用しました。`, 'success');
        } else {
            NotificationManager.show(
                `${successCount}件の修正を適用しました。${errorCount}件でエラーが発生しました。`, 
                'warning'
            );
        }
    }

    // 統計情報を取得
    getStatistics() {
        const total = this.comments.length;
        const applied = this.comments.filter(c => c.applied).length;
        const unapplied = total - applied;
        
        const severityCount = {
            high: this.comments.filter(c => c.severity === 'high').length,
            medium: this.comments.filter(c => c.severity === 'medium').length,
            low: this.comments.filter(c => c.severity === 'low').length
        };

        return {
            total,
            applied,
            unapplied,
            severityCount,
            progress: total > 0 ? (applied / total) * 100 : 0
        };
    }
}

// グローバル関数
function applyComment(commentId, showConfirmation = true) {
    if (window.commentsManager) {
        window.commentsManager.applyComment(commentId, showConfirmation);
    }
}

function ignoreComment(commentId) {
    if (window.commentsManager) {
        window.commentsManager.ignoreComment(commentId);
    }
}

function confirmApply() {
    // モーダル内の確認ボタンがクリックされた時の処理
    // 実際の適用は showConfirmationDialog 内で処理される
}

function filterComments(mode) {
    if (window.commentsManager) {
        window.commentsManager.setFilter(mode);
    }
}

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        CommentsManager, 
        applyComment, 
        ignoreComment, 
        confirmApply, 
        filterComments 
    };
} else {
    window.CommentsManager = CommentsManager;
    window.applyComment = applyComment;
    window.ignoreComment = ignoreComment;
    window.confirmApply = confirmApply;
    window.filterComments = filterComments;
}