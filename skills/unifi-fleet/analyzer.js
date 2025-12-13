// ============================================
// UniFi Fleet Analyzer - Natural Language Query Engine
// ============================================
// Enables dynamic querying of UniFi site data using natural language.
// Parses questions into executable filter/aggregate/sort operations.

class UniFiAnalyzer {
    constructor() {
        this.sites = [];
        this.lastUpdate = null;
    }

    // =============================================
    // Data Loading & Normalization
    // =============================================
    
    loadData(rawSites) {
        this.sites = rawSites.map(site => this.normalizeSite(site));
        this.lastUpdate = new Date();
        console.log(`[Analyzer] Loaded ${this.sites.length} sites at ${this.lastUpdate.toISOString()}`);
        return this.sites.length;
    }

    normalizeSite(site) {
        const meta = site.meta || {};
        const stats = site.statistics || {};
        const counts = stats.counts || {};
        const percentages = stats.percentages || {};
        const wans = stats.wans || {};
        const ispInfo = stats.ispInfo || {};
        
        // Extract WAN details
        const wanEntries = Object.entries(wans);
        const wanDetails = wanEntries.map(([name, data]) => ({
            name,
            uptime: data.wanUptime || 0,
            externalIp: data.externalIp || '',
            isp: data.ispInfo?.name || data.ispInfo?.organization || ''
        }));
        
        // Primary ISP
        const primaryIsp = wanDetails.find(w => w.isp)?.isp || ispInfo?.name || ispInfo?.organization || '';
        const primaryUptime = wanDetails[0]?.uptime || 0;

        // Device counts
        const totalDevices = counts.totalDevice || 0;
        const offlineDevices = counts.offlineDevice || 0;
        const onlineDevices = totalDevices - offlineDevices;
        
        // Client counts
        const wifiClients = counts.wifiClient || 0;
        const wiredClients = counts.wiredClient || 0;
        const totalClients = wifiClients + wiredClients;
        
        // Alerts
        const criticalAlerts = counts.criticalNotification || 0;
        const warningAlerts = counts.warningNotification || 0;
        
        // Performance
        const txRetry = percentages.txRetry || 0;
        const satisfaction = percentages.satisfaction || 100;
        
        // Health score
        const deviceOnlinePercent = totalDevices > 0 ? (onlineDevices / totalDevices) * 100 : 100;
        const healthScore = Math.round(
            (deviceOnlinePercent * 0.4) +
            (primaryUptime * 0.3) +
            ((100 - txRetry) * 0.15) +
            ((criticalAlerts === 0 ? 100 : 0) * 0.15)
        );

        return {
            id: site.siteId,
            deviceId: site.deviceId,
            name: meta.desc || meta.name || 'Unknown',
            internalName: meta.name || '',
            timezone: meta.timezone || 'UTC',
            totalDevices,
            offlineDevices,
            onlineDevices,
            wifiDevices: counts.wifiDevice || 0,
            wiredDevices: counts.wiredDevice || 0,
            gatewayDevices: counts.gatewayDevice || 0,
            offlineWifi: counts.offlineWifiDevice || 0,
            offlineWired: counts.offlineWiredDevice || 0,
            offlineGateway: counts.offlineGatewayDevice || 0,
            wifiClients,
            wiredClients,
            totalClients,
            guestClients: counts.guestClient || 0,
            criticalAlerts,
            warningAlerts,
            ssidCount: counts.wlanGroup || counts.ssid || 0,
            vlanCount: counts.vlan || 0,
            isp: primaryIsp,
            wanUptime: primaryUptime,
            externalIp: wanDetails[0]?.externalIp || '',
            wans: wanDetails,
            txRetry,
            satisfaction,
            healthScore,
            deviceOnlinePercent: Math.round(deviceOnlinePercent),
            isHealthy: offlineDevices === 0 && criticalAlerts === 0 && primaryUptime >= 99,
            hasIssues: offlineDevices > 0 || criticalAlerts > 0 || primaryUptime < 95
        };
    }

    // =============================================
    // Core Query Operations
    // =============================================

    filter(predicate) {
        return this.sites.filter(predicate);
    }

    sort(field, order = 'desc') {
        return [...this.sites].sort((a, b) => {
            const va = a[field] ?? 0;
            const vb = b[field] ?? 0;
            return order === 'asc' ? va - vb : vb - va;
        });
    }

    top(n, field) {
        return this.sort(field, 'desc').slice(0, n);
    }

    bottom(n, field) {
        return this.sort(field, 'asc').slice(0, n);
    }

    sum(field) {
        return this.sites.reduce((acc, s) => acc + (s[field] || 0), 0);
    }

    avg(field) {
        if (!this.sites.length) return 0;
        return Math.round(this.sum(field) / this.sites.length * 10) / 10;
    }

    count(predicate = null) {
        return predicate ? this.filter(predicate).length : this.sites.length;
    }

    groupBy(field) {
        const groups = {};
        this.sites.forEach(s => {
            const key = s[field] || 'Unknown';
            if (!groups[key]) groups[key] = [];
            groups[key].push(s);
        });
        return groups;
    }

    findByName(name) {
        const q = name.toLowerCase();
        return this.sites.find(s => 
            s.name.toLowerCase() === q ||
            s.name.toLowerCase().includes(q) ||
            s.internalName.toLowerCase().includes(q)
        );
    }

    search(query) {
        const q = query.toLowerCase();
        return this.sites.filter(s =>
            s.name.toLowerCase().includes(q) ||
            s.internalName.toLowerCase().includes(q) ||
            s.isp.toLowerCase().includes(q)
        );
    }

    // =============================================
    // Fleet Summary
    // =============================================

    summary() {
        const healthy = this.filter(s => s.isHealthy).length;
        const withIssues = this.filter(s => s.hasIssues).length;
        const critical = this.filter(s => s.offlineGateway > 0 || s.criticalAlerts > 0).length;
        
        return {
            totalSites: this.sites.length,
            totalDevices: this.sum('totalDevices'),
            totalClients: this.sum('totalClients'),
            offlineDevices: this.sum('offlineDevices'),
            healthySites: healthy,
            warningSites: withIssues - critical,
            criticalSites: critical,
            avgHealthScore: this.avg('healthScore'),
            avgUptime: this.avg('wanUptime'),
            topIssues: this.filter(s => s.hasIssues)
                .sort((a, b) => b.offlineDevices - a.offlineDevices)
                .slice(0, 5)
                .map(s => ({ name: s.name, offline: s.offlineDevices, alerts: s.criticalAlerts }))
        };
    }

    // =============================================
    // Natural Language Query Engine
    // =============================================

    analyze(query) {
        const q = query.toLowerCase().trim();
        const pred = this.buildPredicate(q);

        // Help
        if (/^(help|commands|\?|what can you)/.test(q)) {
            return { type: 'help' };
        }

        // Rankings: "top N", "worst N", "bottom N"
        const rankMatch = q.match(/(?:top|best|worst|bottom|lowest|highest)\s*(\d+)?/);
        if (rankMatch) {
            const n = parseInt(rankMatch[1]) || 10;
            const sortField = this.detectField(q);
            const isWorst = /worst|bottom|lowest/.test(q);
            const order = isWorst ? 'asc' : 'desc';
            const actualOrder = sortField === 'healthScore' ? (isWorst ? 'asc' : 'desc') : order;
            return { 
                type: 'ranking', 
                order: actualOrder, 
                field: sortField, 
                sites: actualOrder === 'asc' ? this.bottom(n, sortField) : this.top(n, sortField),
                count: n
            };
        }

        // Aggregations: "total X", "average X", "sum X", "how many"
        if (/^(?:total|sum|average|avg|mean)\s+/.test(q) || /how many/.test(q)) {
            const field = this.detectField(q);
            if (/average|avg|mean/.test(q)) {
                return { type: 'aggregate', operation: 'avg', field, value: this.avg(field) };
            }
            if (/how many sites/.test(q)) {
                if (pred) {
                    const count = this.count(pred);
                    return { type: 'aggregate', operation: 'count', field: 'sites', value: count, filtered: true };
                }
                return { type: 'aggregate', operation: 'count', field: 'sites', value: this.sites.length };
            }
            return { type: 'aggregate', operation: 'sum', field, value: this.sum(field) };
        }

        // Site detail: "status of X", "show X", "details for X"
        if (/(?:status|detail|info|show me|how is|what about|check)\s+(?:of\s+|for\s+)?/i.test(q)) {
            const name = this.extractSiteName(q);
            if (name) {
                const site = this.findByName(name);
                if (site) return { type: 'detail', site };
                const suggestions = this.search(name.split(/\s/)[0]).slice(0, 3);
                return { type: 'notfound', query: name, suggestions };
            }
        }

        // Summary: "summary", "overview", "fleet status"
        if (/summary|overview|fleet|everything|all sites|dashboard/.test(q)) {
            return { type: 'summary', data: this.summary() };
        }

        // What's offline / issues
        if (/what.*(offline|down|issue|problem|wrong)/.test(q) || /^offline$/.test(q)) {
            const sites = this.filter(s => s.hasIssues);
            return { type: 'filter', sites, count: sites.length, query: 'sites with issues' };
        }

        // Filter query with predicate
        if (pred) {
            const sites = this.filter(pred);
            return { type: 'filter', sites, count: sites.length, query: q };
        }

        // Fallback: search by name
        const searchResults = this.search(q);
        if (searchResults.length > 0) {
            return { type: 'search', sites: searchResults, count: searchResults.length, query: q };
        }

        return { type: 'unknown', query: q };
    }

    // =============================================
    // Field Detection from Natural Language
    // =============================================

    detectField(q) {
        const fieldMap = [
            [/offline\s*device|devices?\s*offline|down/, 'offlineDevices'],
            [/total\s*device|all\s*device|device\s*count/, 'totalDevices'],
            [/online\s*device|devices?\s*online|up/, 'onlineDevices'],
            [/wifi\s*device|access\s*point|aps?(?:\s|$)/, 'wifiDevices'],
            [/wired\s*device|switch/, 'wiredDevices'],
            [/gateway|udm|usg|router/, 'gatewayDevices'],
            [/wifi\s*client|wireless\s*client/, 'wifiClients'],
            [/wired\s*client/, 'wiredClients'],
            [/client|user|connected|connection/, 'totalClients'],
            [/guest/, 'guestClients'],
            [/critical|alert/, 'criticalAlerts'],
            [/warning/, 'warningAlerts'],
            [/uptime|wan/, 'wanUptime'],
            [/retry|tx\s*retry|wifi\s*quality/, 'txRetry'],
            [/health|score/, 'healthScore'],
            [/satisfaction/, 'satisfaction'],
            [/ssid|wireless\s*network/, 'ssidCount'],
            [/vlan/, 'vlanCount'],
        ];

        for (const [pattern, field] of fieldMap) {
            if (pattern.test(q)) return field;
        }
        return 'totalClients';
    }

    // =============================================
    // Predicate Builder - Natural Language to Filters
    // =============================================

    buildPredicate(q) {
        const predicates = [];

        // Numeric comparisons
        const numericPatterns = [
            [/more than (\d+)/i, '>'],
            [/greater than (\d+)/i, '>'],
            [/over (\d+)/i, '>'],
            [/above (\d+)/i, '>'],
            [/exceeds? (\d+)/i, '>'],
            [/at least (\d+)/i, '>='],
            [/(\d+)\s*\+/i, '>='],
            [/(\d+)\s*or more/i, '>='],
            [/minimum (\d+)/i, '>='],
            [/less than (\d+)/i, '<'],
            [/under (\d+)/i, '<'],
            [/below (\d+)/i, '<'],
            [/fewer than (\d+)/i, '<'],
            [/at most (\d+)/i, '<='],
            [/up to (\d+)/i, '<='],
            [/maximum (\d+)/i, '<='],
            [/exactly (\d+)/i, '==='],
            [/equal to (\d+)/i, '==='],
        ];

        for (const [pattern, operator] of numericPatterns) {
            const match = q.match(pattern);
            if (match) {
                const num = parseInt(match[1]);
                const field = this.detectField(q);
                predicates.push(site => {
                    const val = site[field] ?? 0;
                    switch (operator) {
                        case '>': return val > num;
                        case '>=': return val >= num;
                        case '<': return val < num;
                        case '<=': return val <= num;
                        case '===': return val === num;
                        default: return true;
                    }
                });
                break;
            }
        }

        // Status filters
        if (/(?:^|\s)(offline|down|issue|problem|unhealthy)/.test(q) && !/not\s+(offline|down)/.test(q)) {
            predicates.push(s => s.hasIssues);
        }
        if (/(?:^|\s)(healthy|online|working|good|up)(?:\s|$)/.test(q) && !/un/.test(q)) {
            predicates.push(s => s.isHealthy);
        }
        if (/critical\s*alert|alert.*critical/.test(q)) {
            predicates.push(s => s.criticalAlerts > 0);
        }
        if (/no\s*issue|no\s*problem|without\s*issue/.test(q)) {
            predicates.push(s => !s.hasIssues);
        }

        // ISP filters
        const ispPatterns = [
            [/verizon/i, /verizon/i],
            [/lumen|level\s*3|centurylink/i, /lumen|level\s*3|centurylink/i],
            [/at\s*&?\s*t(?:\s|$)/i, /at&?t/i],
            [/spectrum|charter/i, /spectrum|charter/i],
            [/comcast|xfinity/i, /comcast|xfinity/i],
            [/cox/i, /cox/i],
            [/mediacom/i, /mediacom/i],
            [/brightspeed/i, /brightspeed/i],
        ];

        for (const [queryPattern, ispPattern] of ispPatterns) {
            if (queryPattern.test(q)) {
                predicates.push(s => s.isp && ispPattern.test(s.isp));
                break;
            }
        }

        // Site name patterns
        const namePatterns = [
            'setco', 'hoods', 'kinder', 'anne', 'celebration', 'jubilee', 
            'tracery', 'coastal', 'fairhope', 'freeport', 'panama', 
            'destin', 'pensacola', 'dirt', 'fulcrum', 'clauger', 'obera'
        ];
        
        for (const name of namePatterns) {
            if (q.includes(name)) {
                predicates.push(s => s.name.toLowerCase().includes(name));
                break;
            }
        }

        if (predicates.length === 0) return null;
        return site => predicates.every(p => p(site));
    }

    // =============================================
    // Helper: Extract Site Name from Query
    // =============================================

    extractSiteName(q) {
        const quoted = q.match(/["']([^"']+)["']/);
        if (quoted) return quoted[1];

        const patterns = [
            /status\s+(?:of\s+)?(.+?)(?:\?|$)/i,
            /details?\s+(?:for\s+)?(.+?)(?:\?|$)/i,
            /show\s+(?:me\s+)?(.+?)(?:\?|$)/i,
            /how\s+is\s+(.+?)(?:\?|$)/i,
            /what\s+about\s+(.+?)(?:\?|$)/i,
            /check\s+(?:on\s+)?(.+?)(?:\?|$)/i,
            /info\s+(?:on\s+|for\s+)?(.+?)(?:\?|$)/i,
        ];

        for (const pattern of patterns) {
            const match = q.match(pattern);
            if (match) {
                let name = match[1].trim();
                name = name.replace(/\s+(site|location|office|branch)$/i, '');
                return name;
            }
        }

        return null;
    }
}

// =============================================
// Response Formatter
// =============================================

class ResponseFormatter {
    
    static formatSiteDetail(site) {
        const healthEmoji = site.healthScore >= 90 ? '🟢' : site.healthScore >= 70 ? '🟡' : '🔴';
        
        return `📍 <strong>${site.name}</strong>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Health Score: <span class="highlight">${site.healthScore}%</span> ${healthEmoji}
ISP: ${site.isp || 'Unknown'} | Uptime: ${site.wanUptime}%

<strong>Devices:</strong> ${site.onlineDevices}/${site.totalDevices} online
  • APs: ${site.wifiDevices} (${site.offlineWifi} offline)
  • Switches: ${site.wiredDevices} (${site.offlineWired} offline)
  • Gateways: ${site.gatewayDevices} (${site.offlineGateway} offline)

<strong>Clients:</strong> ${site.totalClients} connected
  • WiFi: ${site.wifiClients} | Wired: ${site.wiredClients} | Guest: ${site.guestClients}

Alerts: ${site.criticalAlerts} critical, ${site.warningAlerts} warnings
Networks: ${site.ssidCount} SSIDs, ${site.vlanCount} VLANs
IP: ${site.externalIp || 'N/A'}`;
    }

    static formatSummary(data) {
        const healthyPct = Math.round(data.healthySites / data.totalSites * 100);
        
        let response = `🌐 <strong>OberaConnect Fleet Status</strong>
━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sites: <span class="highlight">${data.totalSites}</span> | Devices: <span class="highlight">${data.totalDevices}</span> | Clients: <span class="highlight">${data.totalClients.toLocaleString()}</span>
Offline Devices: <span class="highlight">${data.offlineDevices}</span>

<strong>Health Overview:</strong>
  🟢 Healthy: ${data.healthySites} sites (${healthyPct}%)
  🟡 Warning: ${data.warningSites} sites
  🔴 Critical: ${data.criticalSites} sites

Avg Health Score: ${data.avgHealthScore}% | Avg Uptime: ${data.avgUptime}%`;

        if (data.topIssues.length > 0) {
            response += `\n\n<strong>Top Issues:</strong>`;
            data.topIssues.forEach((issue, i) => {
                response += `\n  ${i + 1}. ${issue.name} - ${issue.offline} offline, ${issue.alerts} alerts`;
            });
        }

        return response;
    }

    static formatFilterResults(sites, query) {
        if (sites.length === 0) {
            return `No sites found matching "${query}"`;
        }

        let response = `Found <span class="highlight">${sites.length}</span> sites matching "${query}":\n`;
        
        const display = sites.slice(0, 15);
        display.forEach((site, i) => {
            const status = site.hasIssues ? '🔴' : '🟢';
            response += `\n${i + 1}. ${status} ${site.name}`;
            if (site.offlineDevices > 0) response += ` (${site.offlineDevices} offline)`;
            else response += ` (${site.totalClients} clients)`;
        });

        if (sites.length > 15) {
            response += `\n\n... and ${sites.length - 15} more`;
        }

        return response;
    }

    static formatRanking(sites, field, order, count) {
        const labels = {
            totalClients: 'clients',
            offlineDevices: 'offline devices',
            healthScore: 'health score',
            wanUptime: 'uptime',
            totalDevices: 'devices',
            txRetry: 'TX retry %',
            criticalAlerts: 'critical alerts'
        };
        
        const label = labels[field] || field;
        const isWorst = order === 'asc';
        const title = isWorst ? `⚠️ Sites with lowest ${label}` : `🏆 Top ${count} sites by ${label}`;

        let response = `${title}:\n`;
        sites.forEach((site, i) => {
            const val = site[field];
            const suffix = field === 'wanUptime' || field === 'healthScore' || field === 'txRetry' ? '%' : '';
            response += `\n${i + 1}. ${site.name}: ${val}${suffix}`;
        });

        return response;
    }

    static formatAggregate(operation, field, value, filtered = false) {
        const labels = {
            totalClients: 'clients',
            offlineDevices: 'offline devices',
            totalDevices: 'devices',
            healthScore: 'health score',
            wanUptime: 'uptime',
            sites: 'sites'
        };
        
        const label = labels[field] || field;
        const suffix = (field === 'wanUptime' || field === 'healthScore') ? '%' : '';
        
        if (operation === 'count') {
            return `📊 <span class="highlight">${value}</span> ${label}${filtered ? ' matching your criteria' : ' total'}`;
        }
        if (operation === 'avg') {
            return `📊 Average ${label}: <span class="highlight">${value}${suffix}</span>`;
        }
        return `📊 Total ${label}: <span class="highlight">${value.toLocaleString()}${suffix}</span>`;
    }

    static formatHelp() {
        return `🤖 <strong>UniFi Fleet Query Engine</strong>

<strong>Status Queries:</strong>
• "What's offline?" - Sites with issues
• "Show healthy sites" - Sites with no issues
• "Summary" / "Fleet status" - Overview

<strong>Filters:</strong>
• "Sites with more than 5 offline devices"
• "Under 95% uptime"
• "Verizon customers"
• "Setco sites"

<strong>Rankings:</strong>
• "Top 10 by clients"
• "Worst uptime"
• "Bottom 5 health score"

<strong>Aggregations:</strong>
• "Total clients"
• "Average health score"
• "How many sites have issues"

<strong>Site Details:</strong>
• "Status of [site name]"
• "Show Celebration Church"`;
    }

    static formatNotFound(query, suggestions) {
        let response = `❌ Couldn't find site "${query}"`;
        if (suggestions.length > 0) {
            response += `\n\nDid you mean:`;
            suggestions.forEach(s => {
                response += `\n• ${s.name}`;
            });
        }
        return response;
    }

    static formatUnknown(query) {
        return `🤔 I didn't understand "${query}"\n\nTry asking about:\n• "What's offline?"\n• "Top 10 by clients"\n• "Status of [site name]"\n• "Summary"\n\nOr type "help" for more options.`;
    }

    static format(result) {
        switch (result.type) {
            case 'detail':
                return this.formatSiteDetail(result.site);
            case 'summary':
                return this.formatSummary(result.data);
            case 'filter':
            case 'search':
                return this.formatFilterResults(result.sites, result.query);
            case 'ranking':
                return this.formatRanking(result.sites, result.field, result.order, result.count);
            case 'aggregate':
                return this.formatAggregate(result.operation, result.field, result.value, result.filtered);
            case 'help':
                return this.formatHelp();
            case 'notfound':
                return this.formatNotFound(result.query, result.suggestions);
            case 'unknown':
            default:
                return this.formatUnknown(result.query);
        }
    }
}

if (typeof module !== 'undefined' && module.exports) {
    module.exports = { UniFiAnalyzer, ResponseFormatter };
}
