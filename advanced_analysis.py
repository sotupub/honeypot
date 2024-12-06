import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from collections import defaultdict
from sklearn.cluster import KMeans
import json

class AdvancedAnalysis:
    def __init__(self, db_connection):
        self.db = db_connection
        self.db.row_factory = sqlite3.Row

    def get_full_analysis(self):
        """Get comprehensive analysis of honeypot data"""
        try:
            cursor = self.db.cursor()
            
            # Get basic summary statistics
            summary = self._get_summary_stats(cursor)
            print("Summary stats:", json.dumps(summary, indent=2))
            
            # Get temporal patterns
            temporal_patterns = self._analyze_temporal_patterns(cursor)
            print("Temporal patterns:", json.dumps(temporal_patterns, indent=2))
            
            # Get attack type distribution
            attack_patterns = self._analyze_attack_patterns(cursor)
            print("Attack patterns:", json.dumps(attack_patterns, indent=2))
            
            # Get geographic patterns (if available)
            geographic_patterns = self._analyze_geographic_patterns(cursor)
            
            # Get anomaly statistics
            anomaly_stats = self._detect_anomalies(cursor)
            print("Anomaly stats:", json.dumps(anomaly_stats, indent=2))
            
            # Get attack clusters
            cluster_stats = self._analyze_clusters(cursor)
            print("Cluster stats:", json.dumps(cluster_stats, indent=2))
            
            # Get high risk IPs
            high_risk_ips = self._identify_high_risk_ips(cursor)
            print("High risk IPs:", json.dumps(high_risk_ips, indent=2))
            
            # Construct the response exactly matching the frontend interface
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'summary': summary,
                'patterns': {
                    'temporal': temporal_patterns,
                    'attack_types': attack_patterns,
                    'geographic': geographic_patterns,
                    'anomalies': anomaly_stats,
                    'clusters': cluster_stats
                },
                'high_risk_ips': high_risk_ips
            }
            
            print("Final analysis structure:")
            print(json.dumps(analysis, indent=2))
            return analysis
            
        except Exception as e:
            print(f"Error in full analysis: {e}")
            return self._get_default_analysis()

    def _get_summary_stats(self, cursor):
        """Get basic summary statistics"""
        try:
            cursor.execute("SELECT COUNT(*) as total FROM attacks")
            total_attacks = cursor.fetchone()['total']
            
            cursor.execute("SELECT COUNT(DISTINCT ip_address) as unique_ips FROM attacks")
            unique_ips = cursor.fetchone()['unique_ips']
            
            cursor.execute("SELECT COUNT(*) as blocked FROM blocked_ips")
            blocked_ips = cursor.fetchone()['blocked']
            
            # Get anomaly count from anomalies analysis
            anomalies = self._detect_anomalies(cursor)
            
            return {
                'total_attacks': int(total_attacks),
                'unique_ips': int(unique_ips),
                'blocked_ips': int(blocked_ips),
                'anomalies_detected': int(anomalies['count'])
            }
        except Exception as e:
            print(f"Error getting summary stats: {e}")
            return {
                'total_attacks': 0,
                'unique_ips': 0,
                'blocked_ips': 0,
                'anomalies_detected': 0
            }

    def _analyze_temporal_patterns(self, cursor):
        """Analyze temporal patterns in attacks"""
        try:
            # Get hourly distribution
            cursor.execute("""
                SELECT strftime('%H', timestamp) as hour,
                       COUNT(*) as count
                FROM attacks
                GROUP BY hour
                ORDER BY hour
            """)
            peak_hours = {str(row['hour']): row['count'] for row in cursor.fetchall()}
            
            # Get daily distribution
            cursor.execute("""
                SELECT strftime('%w', timestamp) as day,
                       COUNT(*) as count
                FROM attacks
                GROUP BY day
                ORDER BY day
            """)
            busiest_days = {str(row['day']): row['count'] for row in cursor.fetchall()}
            
            return {
                'peak_hours': peak_hours,
                'busiest_days': busiest_days
            }
        except Exception as e:
            print(f"Error analyzing temporal patterns: {e}")
            return {'peak_hours': {}, 'busiest_days': {}}

    def _analyze_attack_patterns(self, cursor):
        """Analyze attack type patterns"""
        try:
            # Get attack type distribution
            cursor.execute("""
                SELECT attack_type,
                       COUNT(*) as count
                FROM attacks
                GROUP BY attack_type
            """)
            distribution = {str(row['attack_type']): row['count'] for row in cursor.fetchall()}
            
            # Calculate success rate
            cursor.execute("""
                SELECT CAST(SUM(success) AS FLOAT) / COUNT(*) as rate
                FROM attacks
            """)
            success_rate = cursor.fetchone()['rate'] or 0
            
            return {
                'distribution': distribution,
                'success_rate': float(success_rate)
            }
        except Exception as e:
            print(f"Error analyzing attack patterns: {e}")
            return {'distribution': {}, 'success_rate': 0}

    def _analyze_geographic_patterns(self, cursor):
        """Analyze geographic patterns if available"""
        # This would require GeoIP database integration
        # For now, return None to indicate no geographic data
        return None

    def _detect_anomalies(self, cursor):
        """Detect anomalies in attack patterns"""
        try:
            # Simple anomaly detection based on attack frequency
            cursor.execute("""
                SELECT COUNT(*) as total FROM attacks
                WHERE timestamp >= datetime('now', '-1 hour')
            """)
            recent_count = cursor.fetchone()['total']
            
            cursor.execute("""
                SELECT AVG(hourly_count) as avg_count
                FROM (
                    SELECT COUNT(*) as hourly_count
                    FROM attacks
                    GROUP BY strftime('%Y-%m-%d %H', timestamp)
                )
            """)
            avg_hourly = cursor.fetchone()['avg_count'] or 0
            
            is_anomaly = recent_count > (avg_hourly * 2)  # Simple threshold
            
            return {
                'count': int(1 if is_anomaly else 0),
                'percentage': float(100 if is_anomaly else 0)
            }
        except Exception as e:
            print(f"Error detecting anomalies: {e}")
            return {'count': 0, 'percentage': 0}

    def _analyze_clusters(self, cursor):
        """Analyze attack clusters"""
        try:
            cursor.execute("""
                SELECT attack_type,
                       COUNT(*) as count
                FROM attacks
                GROUP BY attack_type
            """)
            clusters = {str(row['attack_type']): row['count'] for row in cursor.fetchall()}
            
            return {
                'count': len(clusters),
                'distribution': clusters
            }
        except Exception as e:
            print(f"Error analyzing clusters: {e}")
            return {'count': 0, 'distribution': {}}

    def _identify_high_risk_ips(self, cursor):
        """Identify high risk IP addresses"""
        try:
            cursor.execute("""
                SELECT ip_address,
                       COUNT(*) as attack_count,
                       GROUP_CONCAT(DISTINCT attack_type) as attack_types
                FROM attacks
                GROUP BY ip_address
                HAVING attack_count > 5
                ORDER BY attack_count DESC
                LIMIT 10
            """)
            
            high_risk = []
            for row in cursor.fetchall():
                attack_types = row['attack_types'].split(',') if row['attack_types'] else []
                threat_score = row['attack_count'] * len(attack_types)
                high_risk.append({
                    'ip': str(row['ip_address']),
                    'threat_score': float(threat_score),
                    'attack_count': int(row['attack_count']),
                    'attack_types': [str(t) for t in attack_types]
                })
            
            return high_risk
        except Exception as e:
            print(f"Error identifying high risk IPs: {e}")
            return []

    def _get_default_analysis(self):
        """Return default analysis structure when errors occur"""
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_attacks': 0,
                'unique_ips': 0,
                'blocked_ips': 0,
                'anomalies_detected': 0
            },
            'patterns': {
                'temporal': {
                    'peak_hours': {},
                    'busiest_days': {}
                },
                'attack_types': {
                    'distribution': {},
                    'success_rate': 0
                },
                'geographic': None,
                'anomalies': {
                    'count': 0,
                    'percentage': 0
                },
                'clusters': {
                    'count': 0,
                    'distribution': {}
                }
            },
            'high_risk_ips': []
        }
