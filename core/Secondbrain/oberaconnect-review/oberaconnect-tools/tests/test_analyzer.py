"""
Tests for UniFi Fleet Query Engine.

Tests:
- Natural language query parsing
- Filter operations
- Top/bottom rankings
- Grouping and aggregation
"""

import pytest


class TestQueryIntentDetection:
    """Tests for query intent detection."""

    def test_summary_intent(self, sample_sites):
        """Test summary query detection."""
        from unifi.analyzer import UniFiAnalyzer, QueryIntent

        analyzer = UniFiAnalyzer(sample_sites)

        result = analyzer.analyze("show me a summary")
        assert result.intent == QueryIntent.SUMMARY

        result = analyzer.analyze("fleet overview")
        assert result.intent == QueryIntent.SUMMARY

        result = analyzer.analyze("what's the status?")
        assert result.intent == QueryIntent.SUMMARY

    def test_top_query_detection(self, sample_sites):
        """Test top N query detection."""
        from unifi.analyzer import UniFiAnalyzer, QueryIntent

        analyzer = UniFiAnalyzer(sample_sites)

        result = analyzer.analyze("top 5 sites by clients")
        assert result.intent == QueryIntent.TOP

        result = analyzer.analyze("highest 10 by devices")
        assert result.intent == QueryIntent.TOP

    def test_filter_query_detection(self, sample_sites):
        """Test filter query detection."""
        from unifi.analyzer import UniFiAnalyzer, QueryIntent

        analyzer = UniFiAnalyzer(sample_sites)

        result = analyzer.analyze("sites with offline devices")
        assert result.intent == QueryIntent.FILTER

    def test_search_query_detection(self, sample_sites):
        """Test search query detection."""
        from unifi.analyzer import UniFiAnalyzer, QueryIntent

        analyzer = UniFiAnalyzer(sample_sites)

        result = analyzer.analyze("find setco")
        assert result.intent == QueryIntent.SEARCH


class TestFleetSummaryQuery:
    """Tests for summary query results."""

    def test_summary_includes_all_stats(self, sample_sites):
        """Test that summary includes all expected stats."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("summary")

        assert result.success is True
        assert 'totalSites' in result.data
        assert 'totalDevices' in result.data
        assert 'totalClients' in result.data
        assert 'fleetHealthScore' in result.data


class TestTopBottomQueries:
    """Tests for top/bottom ranking queries."""

    def test_top_by_clients(self, sample_sites):
        """Test top sites by client count."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("top 2 sites by clients")

        assert result.success is True
        assert len(result.data) == 2
        # Gulf Shores has 200, Setco has 150
        assert result.data[0]['name'] == 'Gulf Shores Office'
        assert result.data[1]['name'] == 'Setco Industries'

    def test_bottom_by_health(self, sample_sites):
        """Test bottom sites by health score."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("worst 2 by health score")

        assert result.success is True
        assert len(result.data) == 2
        # Gulf Shores: 60, Hoods: 75
        assert result.data[0]['name'] == 'Gulf Shores Office'
        assert result.data[1]['name'] == 'Hoods Discount'

    def test_default_top_count(self, sample_sites):
        """Test default top count when number not specified."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("top sites by devices")

        assert result.success is True
        # Default is 5, but we only have 4 sites
        assert len(result.data) <= 5


class TestFilterQueries:
    """Tests for filter queries."""

    def test_filter_offline_devices(self, sample_sites):
        """Test filtering sites with offline devices."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("sites with offline devices")

        assert result.success is True
        # Hoods (2 offline) and Gulf Shores (4 offline)
        assert len(result.data) == 2
        assert all(s['offlineDevices'] > 0 for s in result.data)

    def test_filter_by_isp(self, sample_sites):
        """Test filtering sites by ISP."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("verizon sites")

        assert result.success is True
        assert len(result.data) == 2
        assert all('Verizon' in s['isp'] for s in result.data)

    def test_filter_by_health_status(self, sample_sites):
        """Test filtering by health status."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("healthy sites")

        assert result.success is True
        assert len(result.data) == 2
        assert all(s['healthStatus'] == 'healthy' for s in result.data)

    def test_filter_with_comparison(self, sample_sites):
        """Test filtering with numeric comparison."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("sites with more than 100 clients")

        assert result.success is True
        assert all(s['totalClients'] > 100 for s in result.data)


class TestSearchQueries:
    """Tests for search queries."""

    def test_search_by_name(self, sample_sites):
        """Test searching sites by name."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("find setco")

        assert result.success is True
        assert len(result.data) == 1
        assert result.data[0]['name'] == 'Setco Industries'

    def test_search_no_match(self, sample_sites):
        """Test search with no matches."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("find nonexistent")

        assert result.success is True
        assert len(result.data) == 0

    def test_search_partial_match(self, sample_sites):
        """Test partial name matching."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("search gulf")

        assert result.success is True
        assert len(result.data) == 1


class TestGroupQueries:
    """Tests for grouping queries."""

    def test_group_by_isp(self, sample_sites):
        """Test grouping sites by ISP."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("group by isp")

        assert result.success is True
        assert result.data['groupedBy'] == 'ISP'
        assert result.data['groups']['Verizon'] == 2
        assert result.data['groups']['AT&T'] == 1


class TestConvenienceMethods:
    """Tests for analyzer convenience methods."""

    def test_filter_method(self, sample_sites):
        """Test programmatic filtering."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.filter(lambda s: s.total_clients > 100)

        assert len(result) == 2

    def test_top_method(self, sample_sites):
        """Test programmatic top N."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.top(2, 'total_clients')

        assert len(result) == 2
        assert result[0].total_clients >= result[1].total_clients

    def test_sum_method(self, sample_sites):
        """Test sum aggregation."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        total = analyzer.sum('total_clients')

        assert total == 460  # 150+80+30+200

    def test_avg_method(self, sample_sites):
        """Test average calculation."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer(sample_sites)
        avg = analyzer.avg('total_clients')

        assert avg == 115.0  # 460/4


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_sites_list(self):
        """Test analyzer with no sites."""
        from unifi.analyzer import UniFiAnalyzer

        analyzer = UniFiAnalyzer([])
        result = analyzer.analyze("summary")

        assert result.success is False
        assert "No site data" in result.message

    def test_unknown_query(self, sample_sites):
        """Test handling of unparseable query."""
        from unifi.analyzer import UniFiAnalyzer, QueryIntent

        analyzer = UniFiAnalyzer(sample_sites)
        result = analyzer.analyze("xyz gibberish query")

        # Should fall back to filter with no matches or return something reasonable
        assert result.success is True
