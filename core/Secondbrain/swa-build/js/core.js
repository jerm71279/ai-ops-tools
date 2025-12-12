/**
 * Core Utilities Module
 * Security, error handling, validation, and fetch utilities
 * @module core
 */

// ========================================
// DEBUG MODE
// ========================================
const DEBUG_MODE = localStorage.getItem('DEBUG_MODE') === 'true';

function debugLog(...args) {
    if (DEBUG_MODE) {
        console.log('[DEBUG]', ...args);
    }
}

// ========================================
// ERROR BOUNDARY SYSTEM
// ========================================

class ErrorBoundary {
    constructor() {
        this.errors = [];
        this.maxErrors = 10;
        this.setupGlobalErrorHandlers();
    }

    setupGlobalErrorHandlers() {
        // Catch unhandled errors
        window.onerror = (message, source, lineno, colno, error) => {
            this.captureError({
                type: 'uncaught',
                message,
                source,
                lineno,
                colno,
                stack: error?.stack
            });
            return false; // Let default handler run too
        };

        // Catch unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.captureError({
                type: 'unhandled_rejection',
                message: event.reason?.message || String(event.reason),
                stack: event.reason?.stack
            });
        });
    }

    captureError(errorInfo) {
        const errorEntry = {
            ...errorInfo,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            userAgent: navigator.userAgent
        };

        this.errors.push(errorEntry);

        // Keep only recent errors
        if (this.errors.length > this.maxErrors) {
            this.errors.shift();
        }

        // Log for debugging
        console.error('[ErrorBoundary]', errorEntry);

        // Persist to localStorage for debugging
        try {
            localStorage.setItem('app_errors', JSON.stringify(this.errors));
        } catch (e) {
            // localStorage might be full
        }
    }

    getErrors() {
        return [...this.errors];
    }

    clearErrors() {
        this.errors = [];
        localStorage.removeItem('app_errors');
    }

    // Wrap async functions with error handling
    wrap(fn, context = 'unknown') {
        return async (...args) => {
            try {
                return await fn(...args);
            } catch (error) {
                this.captureError({
                    type: 'wrapped_error',
                    context,
                    message: error.message,
                    stack: error.stack
                });
                throw error;
            }
        };
    }

    // Safe execution wrapper that doesn't throw
    safeExecute(fn, context = 'unknown', fallback = null) {
        try {
            const result = fn();
            if (result instanceof Promise) {
                return result.catch(error => {
                    this.captureError({
                        type: 'safe_execute_async',
                        context,
                        message: error.message,
                        stack: error.stack
                    });
                    return fallback;
                });
            }
            return result;
        } catch (error) {
            this.captureError({
                type: 'safe_execute',
                context,
                message: error.message,
                stack: error.stack
            });
            return fallback;
        }
    }
}

// Global error boundary instance
const errorBoundary = new ErrorBoundary();

// ========================================
// SECURITY UTILITIES
// ========================================

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    if (text === null || text === undefined) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

/**
 * Safe HTML attribute escaping
 * @param {string} text - Text to escape for attributes
 * @returns {string} Escaped text
 */
function escapeAttr(text) {
    if (text === null || text === undefined) return '';
    return String(text).replace(/[&<>"']/g, m => ({
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    })[m]);
}

// ========================================
// NOTIFICATION SYSTEM
// ========================================

/**
 * Show toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type: 'info', 'success', 'warning', 'error'
 * @param {number} duration - Duration in ms
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Remove existing notifications
    const existing = document.querySelector('.toast-notification');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast-notification toast-${type}`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'polite');
    toast.innerHTML = `
        <span class="toast-icon">${type === 'error' ? '⚠' : type === 'success' ? '✓' : 'ℹ'}</span>
        <span class="toast-message">${escapeHtml(message)}</span>
        <button class="toast-close" onclick="this.parentElement.remove()" aria-label="Close notification">×</button>
    `;
    document.body.appendChild(toast);

    // Auto-remove after duration
    setTimeout(() => toast.remove(), duration);
}

// ========================================
// FETCH WITH RETRY & RATE LIMITING
// ========================================

/**
 * Sleep utility for delays
 * @param {number} ms - Milliseconds to sleep
 * @returns {Promise}
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Fetch with automatic retry and rate limit handling
 * @param {string} url - URL to fetch
 * @param {object} options - Fetch options
 * @param {number} maxRetries - Max retry attempts
 * @returns {Promise<Response>}
 */
async function fetchWithRetry(url, options = {}, maxRetries = 3) {
    let lastError;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            const response = await fetch(url, options);

            // Handle rate limiting (429)
            if (response.status === 429) {
                const retryAfter = parseInt(response.headers.get('Retry-After') || '1', 10);
                const delayMs = Math.min(retryAfter * 1000, 60000); // Max 60 seconds
                console.warn(`Rate limited. Retrying after ${delayMs}ms (attempt ${attempt + 1}/${maxRetries})`);
                showNotification('API rate limit reached. Retrying...', 'warning');
                await sleep(delayMs);
                continue;
            }

            // Handle server errors with retry
            if (response.status >= 500 && attempt < maxRetries - 1) {
                const delayMs = Math.pow(2, attempt) * 1000; // Exponential backoff
                console.warn(`Server error ${response.status}. Retrying after ${delayMs}ms`);
                await sleep(delayMs);
                continue;
            }

            return response;
        } catch (error) {
            lastError = error;

            // Network errors - retry with exponential backoff
            if (attempt < maxRetries - 1) {
                const delayMs = Math.pow(2, attempt) * 1000;
                console.warn(`Network error. Retrying after ${delayMs}ms (attempt ${attempt + 1}/${maxRetries})`);
                await sleep(delayMs);
                continue;
            }
        }
    }

    // All retries failed
    throw lastError || new Error('Request failed after retries');
}

// ========================================
// INPUT VALIDATION
// ========================================

/**
 * Validate item fields
 * @param {object} fields - Fields to validate
 * @param {string} type - Item type ('projects' or 'tickets')
 * @returns {string[]} Array of error messages
 */
function validateItemFields(fields, type) {
    const errors = [];

    // Title validation
    const titleField = type === 'projects' ? 'Title' : 'TicketTitle';
    if (!fields[titleField] || fields[titleField].trim() === '') {
        errors.push('Title is required');
    } else if (fields[titleField].length > 255) {
        errors.push('Title must be 255 characters or less');
    }

    // Description validation
    if (fields.Description && fields.Description.length > 10000) {
        errors.push('Description must be 10,000 characters or less');
    }

    // Date validation
    if (fields.DueDate) {
        const date = new Date(fields.DueDate);
        if (isNaN(date.getTime())) {
            errors.push('Invalid due date format');
        }
    }

    // Percentage validation
    if (fields.PercentComplete !== undefined && fields.PercentComplete !== '') {
        const pct = parseInt(fields.PercentComplete, 10);
        if (isNaN(pct) || pct < 0 || pct > 100) {
            errors.push('Percentage must be between 0 and 100');
        }
    }

    // Budget validation
    if (fields.Budget !== undefined && fields.Budget !== '') {
        const budget = parseFloat(fields.Budget);
        if (isNaN(budget) || budget < 0) {
            errors.push('Budget must be a positive number');
        }
    }

    return errors;
}

/**
 * Validate time entry fields
 * @param {object} entry - Time entry to validate
 * @param {Array} allowedUsers - List of allowed users
 * @returns {string[]} Array of error messages
 */
function validateTimeEntry(entry, allowedUsers) {
    const errors = [];

    // Employee validation
    if (!entry.employee) {
        errors.push('Please select an employee');
    } else if (!allowedUsers.find(u => u.displayName === entry.employee)) {
        errors.push('Invalid employee selected');
    }

    // Date validation
    if (!entry.date) {
        errors.push('Please select a date');
    } else {
        const entryDate = new Date(entry.date);
        const today = new Date();
        today.setHours(23, 59, 59, 999);
        const oneYearAgo = new Date();
        oneYearAgo.setFullYear(today.getFullYear() - 1);

        if (isNaN(entryDate.getTime())) {
            errors.push('Invalid date format');
        } else if (entryDate > today) {
            errors.push('Cannot log time for future dates');
        } else if (entryDate < oneYearAgo) {
            errors.push('Cannot log time more than a year old');
        }
    }

    // Hours validation
    if (!entry.hours || isNaN(entry.hours)) {
        errors.push('Please enter hours worked');
    } else if (entry.hours <= 0 || entry.hours > 24) {
        errors.push('Hours must be between 0 and 24');
    }

    return errors;
}

// ========================================
// UTILITY FUNCTIONS
// ========================================

/**
 * Format date for display
 * @param {string|Date} date - Date to format
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    if (!date) return 'No date';
    const d = new Date(date);
    if (isNaN(d.getTime())) return 'Invalid date';
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

/**
 * Format relative time
 * @param {string|Date} date - Date to format
 * @returns {string} Relative time string
 */
function formatRelativeTime(date) {
    if (!date) return '';
    const d = new Date(date);
    if (isNaN(d.getTime())) return '';

    const now = new Date();
    const diffMs = now - d;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
    return `${Math.floor(diffDays / 365)} years ago`;
}

/**
 * Generate unique ID
 * @returns {string} Unique ID
 */
function generateId() {
    return 'id_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Debounce function
 * @param {Function} fn - Function to debounce
 * @param {number} delay - Delay in ms
 * @returns {Function} Debounced function
 */
function debounce(fn, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn.apply(this, args), delay);
    };
}

/**
 * Throttle function
 * @param {Function} fn - Function to throttle
 * @param {number} limit - Time limit in ms
 * @returns {Function} Throttled function
 */
function throttle(fn, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            fn.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Safe Feather icons replacement
 */
function safeFeatherReplace() {
    errorBoundary.safeExecute(() => {
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }, 'safeFeatherReplace');
}

// ========================================
// EXPORTS
// ========================================

// Make functions available globally for backwards compatibility
window.ECC = window.ECC || {};
Object.assign(window.ECC, {
    // Error handling
    errorBoundary,

    // Debug
    DEBUG_MODE,
    debugLog,

    // Security
    escapeHtml,
    escapeAttr,

    // Notifications
    showNotification,

    // Fetch
    sleep,
    fetchWithRetry,

    // Validation
    validateItemFields,
    validateTimeEntry,

    // Utilities
    formatDate,
    formatRelativeTime,
    generateId,
    debounce,
    throttle,
    safeFeatherReplace
});

// Also expose at window level for existing code compatibility
window.escapeHtml = escapeHtml;
window.escapeAttr = escapeAttr;
window.showNotification = showNotification;
window.sleep = sleep;
window.fetchWithRetry = fetchWithRetry;
window.validateItemFields = validateItemFields;
window.debugLog = debugLog;
window.safeFeatherReplace = safeFeatherReplace;
window.errorBoundary = errorBoundary;
