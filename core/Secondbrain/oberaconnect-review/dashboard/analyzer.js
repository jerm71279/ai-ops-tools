/**
 * UniFi Fleet Query Engine - JavaScript Implementation
 * 
 * Browser-compatible natural language query engine for UniFi fleet data.
 * 
 * Usage:
 *   const analyzer = new UniFiAnalyzer(sites);
 *   const result = analyzer.analyze("show sites with offline devices");
 */

class UniFiAnalyzer {
  constructor(sites = []) {
    this.sites = sites;
    
    // Field mappings from natural language
    this.fieldMappings = {
      'clients': 'totalClients',
      'users': 'totalClients',
      'devices': 'totalDevices',
      'offline': 'offlineDevices',
      'health': 'healthScore',
      'aps': 'apCount',
      'switches': 'switchCount',
      'gateways': 'gatewayCount',
      'isp': 'isp',
      'name': 'name'
    };
    
    // Comparison operators
    this.comparisons = {
      'more than': '>',
      'greater than': '>',
      'over': '>',
      'less than': '<',
      'fewer than': '<',
      'under': '<',
      'at least': '>=',
      'at most': '<=',
      'exactly': '=='
    };
    
    // Known ISPs
    this.knownISPs = ['verizon', 'lumen', 'at&t', 'att', 'spectrum', 'comcast'];
  }
  
  /**
   * Analyze a natural language query
   */
  analyze(query) {
    const q = query.toLowerCase().trim();
    
    if (this.isSummaryQuery(q)) {
      return this.handleSummary();
    }
    
    if (this.isTopBottomQuery(q)) {
      return this.handleTopBottom(q);
    }
    
    if (this.isGroupQuery(q)) {
      return this.handleGroup(q);
    }
    
    if (this.isSearchQuery(q)) {
      return this.handleSearch(q);
    }
    
    return this.handleFilter(q);
  }
  
  isSummaryQuery(q) {
    return ['summary', 'overview', 'stats', 'status', 'fleet'].some(kw => q.includes(kw));
  }
  
  isTopBottomQuery(q) {
    return /\b(top|bottom|highest|lowest|best|worst)\s*\d*\b/.test(q);
  }
  
  isGroupQuery(q) {
    return q.includes('group') || q.includes('by isp');
  }
  
  isSearchQuery(q) {
    return ['find', 'search', 'locate'].some(kw => q.includes(kw));
  }
  
  handleSummary() {
    const summary = this.getSummary();
    return {
      success: true,
      intent: 'SUMMARY',
      data: summary,
      message: `Fleet: ${summary.totalSites} sites, ${summary.totalDevices} devices, ${summary.fleetHealthScore}% healthy`,
      siteCount: summary.totalSites
    };
  }
  
  handleTopBottom(query) {
    const match = query.match(/\b(top|bottom|highest|lowest)\s*(\d+)?/);
    if (!match) return this.handleFilter(query);
    
    const direction = match[1];
    const n = parseInt(match[2]) || 5;
    const isTop = ['top', 'highest', 'best'].includes(direction);
    const field = this.detectField(query);
    
    const sorted = [...this.sites].sort((a, b) => {
      const aVal = a[field] || 0;
      const bVal = b[field] || 0;
      return isTop ? bVal - aVal : aVal - bVal;
    }).slice(0, n);
    
    return {
      success: true,
      intent: isTop ? 'TOP' : 'BOTTOM',
      data: sorted,
      message: `${isTop ? 'Top' : 'Bottom'} ${n} sites by ${field}`,
      siteCount: sorted.length
    };
  }
  
  handleGroup(query) {
    const field = query.includes('isp') ? 'isp' : 
                  query.includes('health') ? 'healthStatus' : 'isp';
    
    const groups = {};
    this.sites.forEach(site => {
      const key = site[field] || 'Unknown';
      if (!groups[key]) groups[key] = [];
      groups[key].push(site);
    });
    
    return {
      success: true,
      intent: 'GROUP',
      data: {
        groupedBy: field,
        groups: Object.fromEntries(Object.entries(groups).map(([k, v]) => [k, v.length])),
        details: groups
      },
      message: `Grouped by ${field}: ${Object.keys(groups).length} groups`,
      siteCount: this.sites.length
    };
  }
  
  handleSearch(query) {
    const searchTerm = query.replace(/find|search|locate/g, '').trim().toLowerCase();
    const matches = this.sites.filter(s => 
      s.name.toLowerCase().includes(searchTerm)
    );
    
    return {
      success: true,
      intent: 'SEARCH',
      data: matches,
      message: `Found ${matches.length} site(s) matching '${searchTerm}'`,
      siteCount: matches.length
    };
  }
  
  handleFilter(query) {
    let results = [...this.sites];
    
    // Offline filter
    if (query.includes('offline') || query.includes('down')) {
      if (query.includes('no offline') || query.includes('without')) {
        results = results.filter(s => s.offlineDevices === 0);
      } else {
        results = results.filter(s => s.offlineDevices > 0);
      }
    }
    
    // Numeric comparison
    const predicate = this.buildPredicate(query);
    if (predicate) {
      results = results.filter(predicate);
    }
    
    // ISP filter
    for (const isp of this.knownISPs) {
      if (query.includes(isp)) {
        results = results.filter(s => 
          s.isp && s.isp.toLowerCase().includes(isp.replace('att', 'at&t'))
        );
        break;
      }
    }
    
    // Health filter
    if (query.includes('healthy')) {
      results = results.filter(s => s.healthStatus === 'healthy');
    } else if (query.includes('critical')) {
      results = results.filter(s => s.healthStatus === 'critical');
    }
    
    return {
      success: true,
      intent: 'FILTER',
      data: results,
      message: `Found ${results.length} sites matching criteria`,
      siteCount: results.length
    };
  }
  
  buildPredicate(query) {
    for (const [phrase, op] of Object.entries(this.comparisons)) {
      const pattern = new RegExp(`${phrase}\\s*(\\d+)\\s*(\\w+)`);
      const match = query.match(pattern);
      if (match) {
        const value = parseInt(match[1]);
        const fieldWord = match[2].toLowerCase();
        const field = this.mapField(fieldWord);
        if (field) {
          return this.makeComparison(field, op, value);
        }
      }
    }
    return null;
  }
  
  makeComparison(field, op, value) {
    return (site) => {
      const siteValue = site[field] || 0;
      switch (op) {
        case '>': return siteValue > value;
        case '<': return siteValue < value;
        case '>=': return siteValue >= value;
        case '<=': return siteValue <= value;
        case '==': return siteValue === value;
        default: return true;
      }
    };
  }
  
  detectField(query) {
    const q = query.toLowerCase();
    for (const [word, field] of Object.entries(this.fieldMappings)) {
      if (q.includes(word)) return field;
    }
    return 'totalDevices';
  }
  
  mapField(word) {
    return this.fieldMappings[word.toLowerCase()];
  }
  
  getSummary() {
    const summary = {
      totalSites: this.sites.length,
      healthySites: 0,
      warningSites: 0,
      criticalSites: 0,
      totalDevices: 0,
      offlineDevices: 0,
      totalClients: 0,
      totalAPs: 0,
      totalSwitches: 0,
      totalGateways: 0,
      sitesByISP: {}
    };
    
    this.sites.forEach(site => {
      summary.totalDevices += site.totalDevices || 0;
      summary.offlineDevices += site.offlineDevices || 0;
      summary.totalClients += site.totalClients || 0;
      summary.totalAPs += site.apCount || 0;
      summary.totalSwitches += site.switchCount || 0;
      summary.totalGateways += site.gatewayCount || 0;
      
      const health = site.healthStatus || 'unknown';
      if (health === 'healthy') summary.healthySites++;
      else if (health === 'warning') summary.warningSites++;
      else summary.criticalSites++;
      
      const isp = site.isp || 'Unknown';
      summary.sitesByISP[isp] = (summary.sitesByISP[isp] || 0) + 1;
    });
    
    summary.fleetHealthScore = summary.totalSites > 0 
      ? Math.round((summary.healthySites / summary.totalSites) * 100)
      : 100;
    
    return summary;
  }
  
  // Convenience methods
  filter(predicate) { return this.sites.filter(predicate); }
  sort(field, reverse = false) {
    return [...this.sites].sort((a, b) => {
      const diff = (a[field] || 0) - (b[field] || 0);
      return reverse ? -diff : diff;
    });
  }
  top(n, field) { return this.sort(field, true).slice(0, n); }
  bottom(n, field) { return this.sort(field, false).slice(0, n); }
  findByName(name) { return this.sites.find(s => s.name.toLowerCase() === name.toLowerCase()); }
  search(term) { return this.sites.filter(s => s.name.toLowerCase().includes(term.toLowerCase())); }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { UniFiAnalyzer };
}
