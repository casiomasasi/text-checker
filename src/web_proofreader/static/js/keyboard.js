/* キーボードナビゲーション機能 */

class KeyboardNavigationManager {
    constructor() {
        this.isEnabled = true;
        this.currentFocusIndex = -1;
        this.focusableElements = [];
        
        this.init();
    }

    init() {
        this.setupGlobalKeyboardHandlers();
        this.updateFocusableElements();
        
        // DOM変更を監視してフォーカス可能要素を更新
        this.observeDOM();
    }

    setupGlobalKeyboardHandlers() {
        document.addEventListener('keydown', (event) => {
            if (!this.isEnabled) return;
            
            this.handleGlobalKeyDown(event);
        });

        // フォーカス管理
        document.addEventListener('focusin', (event) => {
            this.updateCurrentFocus(event.target);
        });

        // マウスクリックでキーボードナビゲーションを一時的に無効化
        document.addEventListener('mousedown', () => {
            this.temporaryDisable();
        });
    }

    handleGlobalKeyDown(event) {
        // モーダルが開いている場合は処理をスキップ
        if (document.querySelector('.modal.show')) {
            return;
        }

        // 入力フィールドにフォーカスがある場合は一部のキーのみ処理
        if (this.isInputFocused()) {
            this.handleInputKeyDown(event);
            return;
        }

        switch (event.key) {
            case 'Tab':
                this.handleTabNavigation(event);
                break;
            case 'ArrowUp':
                event.preventDefault();
                this.navigateComments(-1);
                break;
            case 'ArrowDown':
                event.preventDefault();
                this.navigateComments(1);
                break;
            case 'Enter':
                event.preventDefault();
                this.handleEnterKey();
                break;
            case 'Escape':
                event.preventDefault();
                this.handleEscapeKey();
                break;
            case ' ':
                if (!this.isInputFocused()) {
                    event.preventDefault();
                    this.handleSpaceKey();
                }
                break;
            case 'Home':
                event.preventDefault();
                this.navigateToFirst();
                break;
            case 'End':
                event.preventDefault();
                this.navigateToLast();
                break;
        }

        // Ctrl/Cmd + キーの組み合わせ
        if (event.ctrlKey || event.metaKey) {
            this.handleControlKeyDown(event);
        }
    }

    handleInputKeyDown(event) {
        // 入力フィールド内でも有効なキー操作
        switch (event.key) {
            case 'Escape':
                event.preventDefault();
                this.blurCurrentInput();
                break;
        }
    }

    handleTabNavigation(event) {
        event.preventDefault();
        
        const direction = event.shiftKey ? -1 : 1;
        this.navigateFocusable(direction);
    }

    handleEnterKey() {
        const focusedElement = document.activeElement;
        
        // コメントカードにフォーカスがある場合
        if (focusedElement.classList.contains('comment-card')) {
            const commentId = focusedElement.getAttribute('data-comment-id');
            if (commentId && window.applyComment) {
                window.applyComment(commentId);
            }
        }
        
        // ハイライトされたテキストにフォーカスがある場合
        if (focusedElement.classList.contains('text-highlight')) {
            const commentId = focusedElement.getAttribute('data-comment-id');
            if (commentId && window.applyComment) {
                window.applyComment(commentId);
            }
        }
        
        // ボタンにフォーカスがある場合
        if (focusedElement.tagName === 'BUTTON') {
            focusedElement.click();
        }
    }

    handleEscapeKey() {
        const focusedElement = document.activeElement;
        
        // コメントカードにフォーカスがある場合
        if (focusedElement.classList.contains('comment-card')) {
            const commentId = focusedElement.getAttribute('data-comment-id');
            if (commentId && window.ignoreComment) {
                window.ignoreComment(commentId);
            }
        }
        
        // ハイライトされたテキストにフォーカスがある場合
        if (focusedElement.classList.contains('text-highlight')) {
            const commentId = focusedElement.getAttribute('data-comment-id');
            if (commentId && window.ignoreComment) {
                window.ignoreComment(commentId);
            }
        }
        
        // 選択をクリア
        if (window.commentsManager) {
            window.commentsManager.clearSelection();
        }
        
        // フォーカスをエディタに移動
        this.focusEditor();
    }

    handleSpaceKey() {
        const focusedElement = document.activeElement;
        
        // コメントカードまたはハイライトで Enter と同じ動作
        if (focusedElement.classList.contains('comment-card') || 
            focusedElement.classList.contains('text-highlight')) {
            this.handleEnterKey();
        }
    }

    handleControlKeyDown(event) {
        switch (event.key.toLowerCase()) {
            case 's':
                event.preventDefault();
                if (window.textEditor && typeof window.textEditor.save === 'function') {
                    window.textEditor.save();
                }
                break;
            case 'd':
                event.preventDefault();
                if (typeof window.downloadDocument === 'function') {
                    window.downloadDocument();
                }
                break;
            case 'a':
                if (!this.isInputFocused()) {
                    event.preventDefault();
                    if (typeof window.applyAllComments === 'function') {
                        window.applyAllComments();
                    }
                }
                break;
            case '/':
                event.preventDefault();
                if (typeof window.showKeyboardHelp === 'function') {
                    window.showKeyboardHelp();
                }
                break;
            case '1':
                event.preventDefault();
                this.setCommentFilter('all');
                break;
            case '2':
                event.preventDefault();
                this.setCommentFilter('unapplied');
                break;
        }
    }

    navigateComments(direction) {
        if (!window.commentsManager) return;
        
        window.commentsManager.navigateComment(direction);
    }

    navigateFocusable(direction) {
        this.updateFocusableElements();
        
        if (this.focusableElements.length === 0) return;
        
        let newIndex = this.currentFocusIndex + direction;
        
        // 循環ナビゲーション
        if (newIndex < 0) {
            newIndex = this.focusableElements.length - 1;
        } else if (newIndex >= this.focusableElements.length) {
            newIndex = 0;
        }
        
        this.focusElementAt(newIndex);
    }

    navigateToFirst() {
        if (this.focusableElements.length > 0) {
            this.focusElementAt(0);
        }
    }

    navigateToLast() {
        if (this.focusableElements.length > 0) {
            this.focusElementAt(this.focusableElements.length - 1);
        }
    }

    updateFocusableElements() {
        const selectors = [
            '.comment-card',
            '.text-highlight',
            'button:not([disabled])',
            'input:not([disabled])',
            'select:not([disabled])',
            'textarea:not([disabled])',
            'a[href]',
            '[tabindex]:not([tabindex="-1"])'
        ];
        
        this.focusableElements = Array.from(document.querySelectorAll(selectors.join(', ')))
            .filter(el => this.isElementVisible(el))
            .sort((a, b) => this.getTabIndex(a) - this.getTabIndex(b));
    }

    isElementVisible(element) {
        const rect = element.getBoundingClientRect();
        const style = window.getComputedStyle(element);
        
        return (
            rect.width > 0 &&
            rect.height > 0 &&
            style.visibility !== 'hidden' &&
            style.display !== 'none' &&
            style.opacity !== '0'
        );
    }

    getTabIndex(element) {
        const tabIndex = element.getAttribute('tabindex');
        return tabIndex ? parseInt(tabIndex, 10) : 0;
    }

    focusElementAt(index) {
        if (index >= 0 && index < this.focusableElements.length) {
            const element = this.focusableElements[index];
            element.focus();
            this.currentFocusIndex = index;
            
            // スクロールして表示
            element.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest'
            });
        }
    }

    updateCurrentFocus(element) {
        const index = this.focusableElements.indexOf(element);
        if (index !== -1) {
            this.currentFocusIndex = index;
        }
    }

    isInputFocused() {
        const focusedElement = document.activeElement;
        return (
            focusedElement &&
            (focusedElement.tagName === 'INPUT' ||
             focusedElement.tagName === 'TEXTAREA' ||
             focusedElement.contentEditable === 'true')
        );
    }

    blurCurrentInput() {
        if (this.isInputFocused()) {
            document.activeElement.blur();
        }
    }

    focusEditor() {
        const editor = document.getElementById('textEditor');
        if (editor) {
            editor.focus();
        }
    }

    setCommentFilter(mode) {
        if (window.filterComments) {
            window.filterComments(mode);
        }
    }

    temporaryDisable() {
        this.isEnabled = false;
        
        // 少し待ってから再有効化
        setTimeout(() => {
            this.isEnabled = true;
        }, 100);
    }

    observeDOM() {
        const observer = new MutationObserver(() => {
            // DOM変更時にフォーカス可能要素を更新
            Utils.debounce(() => {
                this.updateFocusableElements();
            }, 100)();
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true,
            attributes: true,
            attributeFilter: ['tabindex', 'disabled', 'style', 'class']
        });
    }

    // 外部から呼び出し可能なメソッド
    enable() {
        this.isEnabled = true;
    }

    disable() {
        this.isEnabled = false;
    }

    focusNextComment() {
        this.navigateComments(1);
    }

    focusPreviousComment() {
        this.navigateComments(-1);
    }

    focusFirstComment() {
        const commentElements = document.querySelectorAll('.comment-card');
        if (commentElements.length > 0) {
            commentElements[0].focus();
        }
    }

    focusLastComment() {
        const commentElements = document.querySelectorAll('.comment-card');
        if (commentElements.length > 0) {
            commentElements[commentElements.length - 1].focus();
        }
    }
}

// ヘルプシステム
class KeyboardHelpManager {
    constructor() {
        this.shortcuts = new Map();
        this.registerDefaultShortcuts();
    }

    registerDefaultShortcuts() {
        // 基本ナビゲーション
        this.register('↑ ↓', 'コメント間を移動');
        this.register('Tab', 'フォーカス可能要素間を移動');
        this.register('Shift + Tab', '前のフォーカス可能要素に移動');
        this.register('Home', '最初の要素に移動');
        this.register('End', '最後の要素に移動');
        
        // コメント操作
        this.register('Enter', 'コメントの修正を適用');
        this.register('Space', 'コメントの修正を適用');
        this.register('Esc', 'コメントを無視/選択をクリア');
        
        // エディタ操作
        this.register('Ctrl + S', '文書を保存');
        this.register('Ctrl + Z', '元に戻す');
        this.register('Ctrl + Y', 'やり直し');
        this.register('Ctrl + A', '全選択（テキストエリア内）');
        
        // アプリケーション操作
        this.register('Ctrl + D', '文書をダウンロード');
        this.register('Ctrl + Shift + A', '全ての修正を適用');
        this.register('F1', 'ヘルプを表示');
        this.register('Ctrl + /', 'ヘルプを表示');
        
        // フィルター操作
        this.register('Ctrl + 1', '全てのコメントを表示');
        this.register('Ctrl + 2', '未適用のコメントを表示');
    }

    register(keys, description) {
        this.shortcuts.set(keys, description);
    }

    getShortcutsList() {
        return Array.from(this.shortcuts.entries()).map(([keys, description]) => ({
            keys,
            description
        }));
    }

    updateHelpModal() {
        const helpModal = document.getElementById('keyboardHelpModal');
        if (!helpModal) return;

        const modalBody = helpModal.querySelector('.modal-body');
        if (!modalBody) return;

        const shortcuts = this.getShortcutsList();
        const groupedShortcuts = this.groupShortcuts(shortcuts);

        let html = '';
        for (const [group, items] of Object.entries(groupedShortcuts)) {
            html += `
                <h6><i class="fas fa-${this.getGroupIcon(group)} me-2"></i>${group}</h6>
                <ul class="list-unstyled mb-3">
            `;
            
            items.forEach(({ keys, description }) => {
                const keyElements = keys.split(' ').map(key => 
                    key.includes('+') ? 
                        key.split('+').map(k => `<kbd>${k.trim()}</kbd>`).join(' + ') :
                        `<kbd>${key}</kbd>`
                ).join(' ');
                
                html += `<li>${keyElements} - ${description}</li>`;
            });
            
            html += '</ul>';
        }

        modalBody.innerHTML = html;
    }

    groupShortcuts(shortcuts) {
        const groups = {
            'ナビゲーション': [],
            'コメント操作': [],
            'エディタ操作': [],
            'アプリケーション': []
        };

        shortcuts.forEach(shortcut => {
            if (shortcut.keys.includes('↑') || shortcut.keys.includes('Tab') || 
                shortcut.keys.includes('Home') || shortcut.keys.includes('End')) {
                groups['ナビゲーション'].push(shortcut);
            } else if (shortcut.keys.includes('Enter') || shortcut.keys.includes('Esc') || 
                       shortcut.keys.includes('Space')) {
                groups['コメント操作'].push(shortcut);
            } else if (shortcut.description.includes('元に戻す') || 
                       shortcut.description.includes('やり直し') || 
                       shortcut.description.includes('保存') ||
                       shortcut.description.includes('全選択')) {
                groups['エディタ操作'].push(shortcut);
            } else {
                groups['アプリケーション'].push(shortcut);
            }
        });

        return groups;
    }

    getGroupIcon(groupName) {
        const icons = {
            'ナビゲーション': 'arrows-alt',
            'コメント操作': 'comments',
            'エディタ操作': 'edit',
            'アプリケーション': 'cogs'
        };
        return icons[groupName] || 'question-circle';
    }
}

// グローバル変数とインスタンス
let keyboardManager = null;
let helpManager = null;

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    keyboardManager = new KeyboardNavigationManager();
    helpManager = new KeyboardHelpManager();
    
    // ヘルプモーダルの内容を更新
    helpManager.updateHelpModal();
});

// グローバル関数
function enableKeyboardNavigation() {
    if (keyboardManager) {
        keyboardManager.enable();
    }
}

function disableKeyboardNavigation() {
    if (keyboardManager) {
        keyboardManager.disable();
    }
}

function focusNextComment() {
    if (keyboardManager) {
        keyboardManager.focusNextComment();
    }
}

function focusPreviousComment() {
    if (keyboardManager) {
        keyboardManager.focusPreviousComment();
    }
}

// エクスポート
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { 
        KeyboardNavigationManager, 
        KeyboardHelpManager,
        enableKeyboardNavigation,
        disableKeyboardNavigation,
        focusNextComment,
        focusPreviousComment
    };
} else {
    window.KeyboardNavigationManager = KeyboardNavigationManager;
    window.KeyboardHelpManager = KeyboardHelpManager;
    window.enableKeyboardNavigation = enableKeyboardNavigation;
    window.disableKeyboardNavigation = disableKeyboardNavigation;
    window.focusNextComment = focusNextComment;
    window.focusPreviousComment = focusPreviousComment;
}