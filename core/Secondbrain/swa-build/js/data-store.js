/**
 * Data Store Module
 * Offline-first data persistence with IndexedDB and localStorage fallback
 * @module data-store
 */

// ========================================
// INDEXED DB STORE
// ========================================

class DataStore {
    constructor(dbName = 'EngineeringCommandCenter', version = 1) {
        this.dbName = dbName;
        this.version = version;
        this.db = null;
        this.stores = ['projects', 'tickets', 'tasks', 'timeEntries', 'comments', 'syncQueue'];
        this.isOnline = navigator.onLine;

        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());
    }

    async init() {
        return new Promise((resolve, reject) => {
            if (!window.indexedDB) {
                console.warn('IndexedDB not supported, falling back to localStorage');
                this.useFallback = true;
                resolve();
                return;
            }

            const request = indexedDB.open(this.dbName, this.version);

            request.onerror = () => {
                console.error('IndexedDB error:', request.error);
                this.useFallback = true;
                resolve(); // Don't reject, use fallback
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('IndexedDB initialized');
                resolve();
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Create object stores
                this.stores.forEach(storeName => {
                    if (!db.objectStoreNames.contains(storeName)) {
                        const store = db.createObjectStore(storeName, { keyPath: 'id' });
                        store.createIndex('lastModified', 'lastModified', { unique: false });
                        store.createIndex('syncStatus', 'syncStatus', { unique: false });

                        // Type-specific indexes
                        if (storeName === 'tasks') {
                            store.createIndex('ticketId', 'fields.TicketID', { unique: false });
                            store.createIndex('status', 'fields.Status', { unique: false });
                        }
                        if (storeName === 'tickets') {
                            store.createIndex('projectId', 'fields.ProjectID', { unique: false });
                        }
                        if (storeName === 'timeEntries') {
                            store.createIndex('employee', 'employee', { unique: false });
                            store.createIndex('date', 'date', { unique: false });
                        }
                    }
                });
            };
        });
    }

    // ========================================
    // CRUD OPERATIONS
    // ========================================

    async getAll(storeName) {
        if (this.useFallback) {
            return this.getFromLocalStorage(storeName);
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();

            request.onsuccess = () => resolve(request.result || []);
            request.onerror = () => {
                console.error(`Error getting all from ${storeName}:`, request.error);
                resolve(this.getFromLocalStorage(storeName));
            };
        });
    }

    async get(storeName, id) {
        if (this.useFallback) {
            const data = this.getFromLocalStorage(storeName);
            return data.find(item => item.id === id) || null;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(id);

            request.onsuccess = () => resolve(request.result || null);
            request.onerror = () => {
                console.error(`Error getting ${id} from ${storeName}:`, request.error);
                resolve(null);
            };
        });
    }

    async put(storeName, item) {
        // Add sync metadata
        item.lastModified = new Date().toISOString();
        item.syncStatus = this.isOnline ? 'synced' : 'pending';

        if (this.useFallback) {
            return this.saveToLocalStorage(storeName, item);
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.put(item);

            request.onsuccess = () => {
                // Also save to localStorage as backup
                this.saveToLocalStorageBackup(storeName, item);
                resolve(item);
            };
            request.onerror = () => {
                console.error(`Error putting to ${storeName}:`, request.error);
                // Fallback to localStorage
                this.saveToLocalStorage(storeName, item);
                resolve(item);
            };
        });
    }

    async putAll(storeName, items) {
        const timestamp = new Date().toISOString();
        items = items.map(item => ({
            ...item,
            lastModified: item.lastModified || timestamp,
            syncStatus: 'synced'
        }));

        if (this.useFallback) {
            localStorage.setItem(`ecc_${storeName}`, JSON.stringify(items));
            return items;
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);

            // Clear existing and add all new
            store.clear();
            items.forEach(item => store.put(item));

            transaction.oncomplete = () => {
                // Backup to localStorage
                localStorage.setItem(`ecc_${storeName}`, JSON.stringify(items));
                resolve(items);
            };
            transaction.onerror = () => {
                console.error(`Error putting all to ${storeName}:`, transaction.error);
                localStorage.setItem(`ecc_${storeName}`, JSON.stringify(items));
                resolve(items);
            };
        });
    }

    async delete(storeName, id) {
        if (!this.isOnline) {
            // Queue for sync when back online
            await this.addToSyncQueue('delete', storeName, { id });
        }

        if (this.useFallback) {
            return this.deleteFromLocalStorage(storeName, id);
        }

        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(id);

            request.onsuccess = () => {
                this.deleteFromLocalStorageBackup(storeName, id);
                resolve(true);
            };
            request.onerror = () => {
                console.error(`Error deleting from ${storeName}:`, request.error);
                resolve(false);
            };
        });
    }

    // ========================================
    // SYNC QUEUE FOR OFFLINE OPERATIONS
    // ========================================

    async addToSyncQueue(operation, storeName, data) {
        const queueItem = {
            id: `sync_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
            operation,
            storeName,
            data,
            timestamp: new Date().toISOString(),
            retries: 0
        };

        await this.put('syncQueue', queueItem);
        return queueItem;
    }

    async getSyncQueue() {
        return this.getAll('syncQueue');
    }

    async clearSyncQueue() {
        if (this.useFallback) {
            localStorage.removeItem('ecc_syncQueue');
            return;
        }

        return new Promise((resolve) => {
            const transaction = this.db.transaction(['syncQueue'], 'readwrite');
            const store = transaction.objectStore('syncQueue');
            store.clear();
            transaction.oncomplete = () => resolve();
        });
    }

    async processSyncQueue(syncFunction) {
        if (!this.isOnline) return;

        const queue = await this.getSyncQueue();
        if (queue.length === 0) return;

        console.log(`Processing ${queue.length} queued operations`);

        for (const item of queue) {
            try {
                await syncFunction(item);
                await this.delete('syncQueue', item.id);
            } catch (error) {
                console.error('Sync failed for item:', item, error);
                item.retries++;
                if (item.retries >= 3) {
                    // Move to failed queue or discard
                    await this.delete('syncQueue', item.id);
                } else {
                    await this.put('syncQueue', item);
                }
            }
        }
    }

    // ========================================
    // LOCALSTORAGE FALLBACK
    // ========================================

    getFromLocalStorage(storeName) {
        try {
            const data = localStorage.getItem(`ecc_${storeName}`);
            return data ? JSON.parse(data) : [];
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return [];
        }
    }

    saveToLocalStorage(storeName, item) {
        try {
            const data = this.getFromLocalStorage(storeName);
            const existingIndex = data.findIndex(i => i.id === item.id);
            if (existingIndex >= 0) {
                data[existingIndex] = item;
            } else {
                data.push(item);
            }
            localStorage.setItem(`ecc_${storeName}`, JSON.stringify(data));
            return item;
        } catch (e) {
            console.error('Error saving to localStorage:', e);
            return item;
        }
    }

    saveToLocalStorageBackup(storeName, item) {
        // Just updates the backup, not primary storage
        this.saveToLocalStorage(storeName, item);
    }

    deleteFromLocalStorage(storeName, id) {
        try {
            const data = this.getFromLocalStorage(storeName);
            const filtered = data.filter(i => i.id !== id);
            localStorage.setItem(`ecc_${storeName}`, JSON.stringify(filtered));
            return true;
        } catch (e) {
            console.error('Error deleting from localStorage:', e);
            return false;
        }
    }

    deleteFromLocalStorageBackup(storeName, id) {
        this.deleteFromLocalStorage(storeName, id);
    }

    // ========================================
    // ONLINE/OFFLINE HANDLERS
    // ========================================

    handleOnline() {
        this.isOnline = true;
        console.log('App is online');

        if (window.showNotification) {
            window.showNotification('Back online! Syncing data...', 'success');
        }

        // Dispatch custom event for app to handle
        window.dispatchEvent(new CustomEvent('app:online'));
    }

    handleOffline() {
        this.isOnline = false;
        console.log('App is offline');

        if (window.showNotification) {
            window.showNotification('You are offline. Changes will sync when back online.', 'warning');
        }

        // Dispatch custom event for app to handle
        window.dispatchEvent(new CustomEvent('app:offline'));
    }

    // ========================================
    // CACHE MANAGEMENT
    // ========================================

    async getCacheTimestamp(storeName) {
        const key = `ecc_cache_ts_${storeName}`;
        return localStorage.getItem(key) || null;
    }

    async setCacheTimestamp(storeName) {
        const key = `ecc_cache_ts_${storeName}`;
        localStorage.setItem(key, new Date().toISOString());
    }

    async isCacheStale(storeName, maxAgeMinutes = 5) {
        const timestamp = await this.getCacheTimestamp(storeName);
        if (!timestamp) return true;

        const cacheAge = Date.now() - new Date(timestamp).getTime();
        return cacheAge > maxAgeMinutes * 60 * 1000;
    }

    async clearAllCaches() {
        this.stores.forEach(storeName => {
            localStorage.removeItem(`ecc_${storeName}`);
            localStorage.removeItem(`ecc_cache_ts_${storeName}`);
        });

        if (this.db) {
            for (const storeName of this.stores) {
                try {
                    const transaction = this.db.transaction([storeName], 'readwrite');
                    transaction.objectStore(storeName).clear();
                } catch (e) {
                    console.error(`Error clearing ${storeName}:`, e);
                }
            }
        }
    }
}

// ========================================
// SINGLETON INSTANCE
// ========================================

const dataStore = new DataStore();

// Initialize on load
dataStore.init().then(() => {
    console.log('DataStore ready');
}).catch(err => {
    console.error('DataStore init error:', err);
});

// ========================================
// EXPORTS
// ========================================

window.ECC = window.ECC || {};
window.ECC.dataStore = dataStore;
window.dataStore = dataStore;
