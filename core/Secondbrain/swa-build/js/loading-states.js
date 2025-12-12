/**
 * Loading States Module
 * Skeleton screens, loading indicators, and state management
 * @module loading-states
 */

// ========================================
// LOADING STATE MANAGER
// ========================================

class LoadingStateManager {
    constructor() {
        this.loadingStates = new Map();
        this.injectStyles();
    }

    injectStyles() {
        if (document.getElementById('loading-states-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'loading-states-styles';
        styles.textContent = `
            /* Skeleton Loading Animation */
            @keyframes skeleton-pulse {
                0% { opacity: 1; }
                50% { opacity: 0.4; }
                100% { opacity: 1; }
            }

            @keyframes shimmer {
                0% { background-position: -200% 0; }
                100% { background-position: 200% 0; }
            }

            .skeleton {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
                border-radius: var(--radius-sm, 6px);
            }

            .skeleton-text {
                height: 14px;
                margin-bottom: 8px;
                border-radius: 4px;
            }

            .skeleton-text.short { width: 60%; }
            .skeleton-text.medium { width: 80%; }
            .skeleton-text.long { width: 100%; }

            .skeleton-title {
                height: 24px;
                width: 70%;
                margin-bottom: 16px;
            }

            .skeleton-card {
                background: var(--surface, #fff);
                border-radius: var(--radius-lg, 16px);
                padding: 20px;
                box-shadow: var(--shadow-sm, 0 1px 2px rgba(0,0,0,0.05));
            }

            .skeleton-avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
            }

            .skeleton-button {
                width: 100px;
                height: 36px;
                border-radius: var(--radius-md, 10px);
            }

            .skeleton-badge {
                width: 60px;
                height: 24px;
                border-radius: 12px;
            }

            /* Loading Overlay */
            .loading-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(255, 255, 255, 0.9);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                z-index: 100;
                border-radius: inherit;
            }

            .loading-spinner {
                width: 40px;
                height: 40px;
                border: 3px solid var(--border, #e2e8f0);
                border-top-color: var(--primary, #6366f1);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            .loading-text {
                margin-top: 12px;
                font-size: 14px;
                color: var(--text-secondary, #64748b);
            }

            /* Section Loading */
            .section-loading {
                min-height: 200px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            /* Inline Loading */
            .inline-loading {
                display: inline-flex;
                align-items: center;
                gap: 8px;
            }

            .inline-spinner {
                width: 16px;
                height: 16px;
                border: 2px solid var(--border, #e2e8f0);
                border-top-color: var(--primary, #6366f1);
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            /* Progress Bar */
            .loading-progress {
                width: 100%;
                height: 4px;
                background: var(--border, #e2e8f0);
                border-radius: 2px;
                overflow: hidden;
            }

            .loading-progress-bar {
                height: 100%;
                background: var(--primary, #6366f1);
                border-radius: 2px;
                transition: width 0.3s ease;
            }

            .loading-progress.indeterminate .loading-progress-bar {
                width: 30%;
                animation: progress-indeterminate 1.5s infinite ease-in-out;
            }

            @keyframes progress-indeterminate {
                0% { margin-left: -30%; }
                100% { margin-left: 100%; }
            }

            /* Fade transitions */
            .fade-in {
                animation: fadeIn 0.3s ease;
            }

            .fade-out {
                animation: fadeOut 0.3s ease;
            }

            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }

            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }

            /* Empty States */
            .empty-state {
                text-align: center;
                padding: 48px 24px;
                color: var(--text-muted, #94a3b8);
            }

            .empty-state-icon {
                font-size: 48px;
                margin-bottom: 16px;
                opacity: 0.5;
            }

            .empty-state-title {
                font-size: 18px;
                font-weight: 600;
                color: var(--text-secondary, #64748b);
                margin-bottom: 8px;
            }

            .empty-state-message {
                font-size: 14px;
                max-width: 300px;
                margin: 0 auto;
            }

            /* Error States */
            .error-state {
                text-align: center;
                padding: 48px 24px;
                background: #fef2f2;
                border-radius: var(--radius-lg, 16px);
                border: 1px solid #fecaca;
            }

            .error-state-icon {
                font-size: 48px;
                color: var(--danger, #ef4444);
                margin-bottom: 16px;
            }

            .error-state-title {
                font-size: 18px;
                font-weight: 600;
                color: var(--danger, #ef4444);
                margin-bottom: 8px;
            }

            .error-state-message {
                font-size: 14px;
                color: #b91c1c;
                max-width: 400px;
                margin: 0 auto 16px;
            }

            .error-state-retry {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                background: var(--danger, #ef4444);
                color: white;
                border: none;
                border-radius: var(--radius-md, 10px);
                cursor: pointer;
                font-size: 14px;
                font-weight: 500;
                transition: background 0.2s;
            }

            .error-state-retry:hover {
                background: #dc2626;
            }
        `;
        document.head.appendChild(styles);
    }

    // ========================================
    // SKELETON GENERATORS
    // ========================================

    createSkeleton(type, options = {}) {
        switch (type) {
            case 'card':
                return this.createCardSkeleton(options);
            case 'list':
                return this.createListSkeleton(options);
            case 'table':
                return this.createTableSkeleton(options);
            case 'kanban':
                return this.createKanbanSkeleton(options);
            case 'stats':
                return this.createStatsSkeleton(options);
            default:
                return this.createGenericSkeleton(options);
        }
    }

    createCardSkeleton(options = {}) {
        const count = options.count || 1;
        let html = '';

        for (let i = 0; i < count; i++) {
            html += `
                <div class="skeleton-card">
                    <div class="skeleton skeleton-title"></div>
                    <div class="skeleton skeleton-text long"></div>
                    <div class="skeleton skeleton-text medium"></div>
                    <div class="skeleton skeleton-text short"></div>
                    <div style="display:flex;gap:8px;margin-top:16px;">
                        <div class="skeleton skeleton-badge"></div>
                        <div class="skeleton skeleton-badge"></div>
                    </div>
                </div>
            `;
        }

        return html;
    }

    createListSkeleton(options = {}) {
        const count = options.count || 5;
        let html = '<div class="skeleton-list">';

        for (let i = 0; i < count; i++) {
            html += `
                <div style="display:flex;align-items:center;gap:12px;padding:12px 0;border-bottom:1px solid var(--border);">
                    <div class="skeleton skeleton-avatar"></div>
                    <div style="flex:1;">
                        <div class="skeleton skeleton-text medium"></div>
                        <div class="skeleton skeleton-text short"></div>
                    </div>
                    <div class="skeleton skeleton-badge"></div>
                </div>
            `;
        }

        html += '</div>';
        return html;
    }

    createTableSkeleton(options = {}) {
        const rows = options.rows || 5;
        const cols = options.cols || 4;

        let html = '<table style="width:100%;">';

        // Header
        html += '<thead><tr>';
        for (let c = 0; c < cols; c++) {
            html += '<th style="padding:12px;"><div class="skeleton skeleton-text short"></div></th>';
        }
        html += '</tr></thead>';

        // Body
        html += '<tbody>';
        for (let r = 0; r < rows; r++) {
            html += '<tr>';
            for (let c = 0; c < cols; c++) {
                html += `<td style="padding:12px;"><div class="skeleton skeleton-text ${c === 0 ? 'medium' : 'short'}"></div></td>`;
            }
            html += '</tr>';
        }
        html += '</tbody></table>';

        return html;
    }

    createKanbanSkeleton(options = {}) {
        const columns = options.columns || 3;
        const cardsPerColumn = options.cardsPerColumn || 3;

        let html = '<div style="display:flex;gap:16px;overflow-x:auto;">';

        for (let col = 0; col < columns; col++) {
            html += `
                <div style="flex:0 0 300px;background:var(--surface-dark);padding:16px;border-radius:var(--radius-lg);">
                    <div class="skeleton skeleton-title" style="width:50%;margin-bottom:16px;"></div>
            `;

            for (let card = 0; card < cardsPerColumn; card++) {
                html += `
                    <div class="skeleton-card" style="margin-bottom:12px;">
                        <div class="skeleton skeleton-text long"></div>
                        <div class="skeleton skeleton-text short"></div>
                        <div style="display:flex;gap:8px;margin-top:12px;">
                            <div class="skeleton skeleton-avatar" style="width:24px;height:24px;"></div>
                            <div class="skeleton skeleton-badge"></div>
                        </div>
                    </div>
                `;
            }

            html += '</div>';
        }

        html += '</div>';
        return html;
    }

    createStatsSkeleton(options = {}) {
        const count = options.count || 4;
        let html = '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;">';

        for (let i = 0; i < count; i++) {
            html += `
                <div class="skeleton-card">
                    <div class="skeleton skeleton-text short" style="height:12px;"></div>
                    <div class="skeleton" style="height:32px;width:60%;margin:12px 0;"></div>
                    <div class="skeleton skeleton-text medium" style="height:10px;"></div>
                </div>
            `;
        }

        html += '</div>';
        return html;
    }

    createGenericSkeleton(options = {}) {
        return `
            <div class="skeleton-card">
                <div class="skeleton skeleton-title"></div>
                <div class="skeleton skeleton-text long"></div>
                <div class="skeleton skeleton-text medium"></div>
            </div>
        `;
    }

    // ========================================
    // LOADING OVERLAY
    // ========================================

    showLoading(containerId, message = 'Loading...') {
        const container = document.getElementById(containerId);
        if (!container) return;

        // Store loading state
        this.loadingStates.set(containerId, true);

        // Make container relative for overlay
        const originalPosition = container.style.position;
        container.dataset.originalPosition = originalPosition;
        container.style.position = 'relative';

        // Create overlay
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay fade-in';
        overlay.id = `loading-overlay-${containerId}`;
        overlay.innerHTML = `
            <div class="loading-spinner"></div>
            <div class="loading-text">${message}</div>
        `;

        container.appendChild(overlay);
    }

    hideLoading(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        this.loadingStates.delete(containerId);

        const overlay = document.getElementById(`loading-overlay-${containerId}`);
        if (overlay) {
            overlay.classList.remove('fade-in');
            overlay.classList.add('fade-out');
            setTimeout(() => {
                overlay.remove();
                // Restore original position
                if (container.dataset.originalPosition !== undefined) {
                    container.style.position = container.dataset.originalPosition || '';
                    delete container.dataset.originalPosition;
                }
            }, 300);
        }
    }

    isLoading(containerId) {
        return this.loadingStates.has(containerId);
    }

    // ========================================
    // INLINE LOADING
    // ========================================

    createInlineLoading(message = '') {
        return `
            <span class="inline-loading">
                <span class="inline-spinner"></span>
                ${message ? `<span>${message}</span>` : ''}
            </span>
        `;
    }

    // ========================================
    // PROGRESS BAR
    // ========================================

    showProgress(containerId, indeterminate = true) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const progress = document.createElement('div');
        progress.className = `loading-progress ${indeterminate ? 'indeterminate' : ''}`;
        progress.id = `progress-${containerId}`;
        progress.innerHTML = '<div class="loading-progress-bar" style="width:0%"></div>';

        container.prepend(progress);
        return progress;
    }

    updateProgress(containerId, percent) {
        const progress = document.getElementById(`progress-${containerId}`);
        if (!progress) return;

        progress.classList.remove('indeterminate');
        const bar = progress.querySelector('.loading-progress-bar');
        if (bar) {
            bar.style.width = `${percent}%`;
        }
    }

    hideProgress(containerId) {
        const progress = document.getElementById(`progress-${containerId}`);
        if (progress) {
            progress.remove();
        }
    }

    // ========================================
    // EMPTY STATES
    // ========================================

    createEmptyState(options = {}) {
        const {
            icon = '📭',
            title = 'No items found',
            message = 'There are no items to display.',
            actionText = null,
            actionCallback = null
        } = options;

        let html = `
            <div class="empty-state">
                <div class="empty-state-icon">${icon}</div>
                <div class="empty-state-title">${window.escapeHtml ? window.escapeHtml(title) : title}</div>
                <div class="empty-state-message">${window.escapeHtml ? window.escapeHtml(message) : message}</div>
        `;

        if (actionText && actionCallback) {
            html += `<button class="btn btn-primary" style="margin-top:16px;" onclick="(${actionCallback})()">${window.escapeHtml ? window.escapeHtml(actionText) : actionText}</button>`;
        }

        html += '</div>';
        return html;
    }

    // ========================================
    // ERROR STATES
    // ========================================

    createErrorState(options = {}) {
        const {
            title = 'Something went wrong',
            message = 'An error occurred while loading data.',
            retryCallback = null
        } = options;

        let html = `
            <div class="error-state">
                <div class="error-state-icon">⚠️</div>
                <div class="error-state-title">${window.escapeHtml ? window.escapeHtml(title) : title}</div>
                <div class="error-state-message">${window.escapeHtml ? window.escapeHtml(message) : message}</div>
        `;

        if (retryCallback) {
            html += `
                <button class="error-state-retry" onclick="(${retryCallback})()">
                    <span>↻</span> Try Again
                </button>
            `;
        }

        html += '</div>';
        return html;
    }

    // ========================================
    // BUTTON LOADING STATE
    // ========================================

    setButtonLoading(button, loading = true, loadingText = 'Loading...') {
        if (typeof button === 'string') {
            button = document.getElementById(button);
        }
        if (!button) return;

        if (loading) {
            button.dataset.originalText = button.innerHTML;
            button.disabled = true;
            button.innerHTML = `<span class="inline-spinner"></span> ${loadingText}`;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
            delete button.dataset.originalText;
        }
    }
}

// ========================================
// SINGLETON INSTANCE
// ========================================

const loadingStates = new LoadingStateManager();

// ========================================
// EXPORTS
// ========================================

window.ECC = window.ECC || {};
window.ECC.loadingStates = loadingStates;
window.loadingStates = loadingStates;
