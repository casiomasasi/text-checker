/* 共通JavaScript機能 */

// 共通ユーティリティ関数
const Utils = {
    // APIリクエスト用のヘルパー
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    // エラーメッセージ表示
    showError(message, containerId = 'errorMessage') {
        const container = document.getElementById(containerId);
        if (container) {
            const textElement = container.querySelector('[id$="Text"]');
            if (textElement) {
                textElement.textContent = message;
            }
            container.classList.remove('d-none');
            
            // 自動で隠す
            setTimeout(() => {
                container.classList.add('d-none');
            }, 10000);
        } else {
            console.error('Error container not found:', containerId);
            alert(message); // フォールバック
        }
    },

    // 成功メッセージ表示
    showSuccess(message, containerId = 'successMessage') {
        const container = document.getElementById(containerId);
        if (container) {
            const textElement = container.querySelector('[id$="Text"]');
            if (textElement) {
                textElement.textContent = message;
            }
            container.classList.remove('d-none');
            
            // 自動で隠す
            setTimeout(() => {
                container.classList.add('d-none');
            }, 5000);
        } else {
            console.error('Success container not found:', containerId);
        }
    },

    // メッセージを隠す
    hideMessage(containerId) {
        const container = document.getElementById(containerId);
        if (container) {
            container.classList.add('d-none');
        }
    },

    // ローディング状態の管理
    setLoading(show, text = '処理中...') {
        if (show) {
            showLoading(text);
        } else {
            hideLoading();
        }
    },

    // プログレスバー更新
    updateProgress(percentage, progressBarId = 'progressBar') {
        const progressBar = document.getElementById(progressBarId);
        if (progressBar) {
            progressBar.style.width = `${percentage}%`;
            progressBar.setAttribute('aria-valuenow', percentage);
        }
    },

    // 要素のアニメーション
    animateElement(element, animationClass, duration = 300) {
        element.classList.add(animationClass);
        setTimeout(() => {
            element.classList.remove(animationClass);
        }, duration);
    },

    // 文字列のHTMLエスケープ
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // ファイルサイズを人間が読める形式に変換
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // 時間を相対的な形式で表示
    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = now - date;
        
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(diff / 3600000);
        const days = Math.floor(diff / 86400000);
        
        if (minutes < 1) return 'たった今';
        if (minutes < 60) return `${minutes}分前`;
        if (hours < 24) return `${hours}時間前`;
        return `${days}日前`;
    },

    // デバウンス関数
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // スロットル関数
    throttle(func, limit) {
        let lastFunc;
        let lastRan;
        return function(...args) {
            if (!lastRan) {
                func.apply(this, args);
                lastRan = Date.now();
            } else {
                clearTimeout(lastFunc);
                lastFunc = setTimeout(() => {
                    if ((Date.now() - lastRan) >= limit) {
                        func.apply(this, args);
                        lastRan = Date.now();
                    }
                }, limit - (Date.now() - lastRan));
            }
        };
    }
};

// グローバルエラーハンドラー
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    Utils.showError('予期しないエラーが発生しました。ページを再読み込みしてください。');
});

// 未処理のPromise拒否をキャッチ
window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    Utils.showError('処理中にエラーが発生しました。');
});

// DOM読み込み完了後の共通初期化
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltipの初期化
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // 自動フォーカス要素
    const autoFocusElement = document.querySelector('[data-autofocus]');
    if (autoFocusElement) {
        setTimeout(() => autoFocusElement.focus(), 100);
    }
});

// セッション管理
const SessionManager = {
    // ローカルストレージのキー
    STORAGE_KEY: 'proofreading_session',

    // セッション情報を保存
    save(sessionData) {
        try {
            localStorage.setItem(this.STORAGE_KEY, JSON.stringify({
                ...sessionData,
                timestamp: Date.now()
            }));
        } catch (error) {
            console.error('Failed to save session:', error);
        }
    },

    // セッション情報を取得
    load() {
        try {
            const data = localStorage.getItem(this.STORAGE_KEY);
            if (data) {
                const sessionData = JSON.parse(data);
                
                // 2時間以上古いセッションは削除
                if (Date.now() - sessionData.timestamp > 2 * 60 * 60 * 1000) {
                    this.clear();
                    return null;
                }
                
                return sessionData;
            }
        } catch (error) {
            console.error('Failed to load session:', error);
        }
        return null;
    },

    // セッション情報をクリア
    clear() {
        try {
            localStorage.removeItem(this.STORAGE_KEY);
        } catch (error) {
            console.error('Failed to clear session:', error);
        }
    }
};

// 通知システム
const NotificationManager = {
    // 通知を表示
    show(message, type = 'info', duration = 5000) {
        const container = this.getContainer();
        const notification = this.createElement(message, type);
        
        container.appendChild(notification);
        
        // アニメーション
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // 自動削除
        setTimeout(() => {
            this.remove(notification);
        }, duration);
        
        return notification;
    },

    // 通知コンテナを取得または作成
    getContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                pointer-events: none;
            `;
            document.body.appendChild(container);
        }
        return container;
    },

    // 通知要素を作成
    createElement(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.style.cssText = `
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            margin-bottom: 10px;
            padding: 12px 16px;
            pointer-events: auto;
            opacity: 0;
            transform: translateX(100%);
            transition: all 0.3s ease;
            max-width: 300px;
            word-wrap: break-word;
        `;
        
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            warning: '#ffc107',
            info: '#0dcaf0'
        };
        
        const color = colors[type] || colors.info;
        notification.style.borderLeftColor = color;
        notification.style.borderLeftWidth = '4px';
        
        const icon = this.getIcon(type);
        notification.innerHTML = `
            <div style="display: flex; align-items: center;">
                <i class="${icon}" style="color: ${color}; margin-right: 8px;"></i>
                <span>${Utils.escapeHtml(message)}</span>
                <button onclick="NotificationManager.remove(this.parentElement.parentElement)" 
                        style="background: none; border: none; margin-left: auto; padding: 0 4px; cursor: pointer;">
                    <i class="fas fa-times" style="color: #6c757d;"></i>
                </button>
            </div>
        `;
        
        notification.classList.add('show');
        return notification;
    },

    // アイコンを取得
    getIcon(type) {
        const icons = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        return icons[type] || icons.info;
    },

    // 通知を削除
    remove(notification) {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (notification.parentElement) {
                notification.parentElement.removeChild(notification);
            }
        }, 300);
    }
};

// キーボードショートカット管理
const KeyboardManager = {
    shortcuts: new Map(),

    // ショートカットを登録
    register(key, callback, description = '') {
        this.shortcuts.set(key, { callback, description });
    },

    // ショートカットを削除
    unregister(key) {
        this.shortcuts.delete(key);
    },

    // キーの組み合わせを文字列に変換
    keyToString(event) {
        const parts = [];
        if (event.ctrlKey) parts.push('ctrl');
        if (event.altKey) parts.push('alt');
        if (event.shiftKey) parts.push('shift');
        if (event.metaKey) parts.push('meta');
        
        const key = event.key.toLowerCase();
        if (!['control', 'alt', 'shift', 'meta'].includes(key)) {
            parts.push(key);
        }
        
        return parts.join('+');
    },

    // 初期化
    init() {
        document.addEventListener('keydown', (event) => {
            const keyString = this.keyToString(event);
            const shortcut = this.shortcuts.get(keyString);
            
            if (shortcut) {
                event.preventDefault();
                shortcut.callback(event);
            }
        });
    }
};

// 初期化
KeyboardManager.init();

// 共通ショートカット登録
KeyboardManager.register('f1', () => {
    if (typeof showKeyboardHelp === 'function') {
        showKeyboardHelp();
    }
}, 'ヘルプを表示');

KeyboardManager.register('ctrl+/', () => {
    if (typeof showKeyboardHelp === 'function') {
        showKeyboardHelp();
    }
}, 'ヘルプを表示');

// エクスポート（モジュール環境でない場合）
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Utils, SessionManager, NotificationManager, KeyboardManager };
} else {
    window.Utils = Utils;
    window.SessionManager = SessionManager;
    window.NotificationManager = NotificationManager;
    window.KeyboardManager = KeyboardManager;
}