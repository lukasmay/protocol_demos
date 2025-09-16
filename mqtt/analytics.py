#!/usr/bin/env python3
"""
Analytics Engine - Advanced Factory Analytics
Subscribes to topic 4 (cloud/factory/analytics) and performs advanced analytics,
predictive analysis, and generates insights
"""
import paho.mqtt.client as mqtt
import json
import time
import threading
import statistics
import sqlite3
import math
import os
from datetime import datetime, timedelta

# Configuration
BROKER = os.getenv("BROKER", "localhost")
PORT = int(os.getenv("PORT", "1884"))  # Cloud broker port
CLIENT_ID = "Analytics"
SUBSCRIBE_TOPIC = "cloud/factory/analytics"
DB_FILE = os.getenv("DB_FILE", "analytics.db")
ANALYSIS_INTERVAL = 30  # seconds

class AnalyticsEngine:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Analytics state
        self.connected = False
        self.message_count = 0
        self.analytics_buffer = []
        self.predictions = {}
        
        # Database connection
        self.db_connection = None
        self.init_database()
        
    def init_database(self):
        """Initialize analytics database"""
        try:
            self.db_connection = sqlite3.connect(DB_FILE, check_same_thread=False)
            cursor = self.db_connection.cursor()
            
            # Analytics data table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analytics_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    energy_efficiency REAL,
                    environmental_comfort REAL,
                    power_consumption_avg REAL,
                    power_factor_avg REAL,
                    temperature_avg REAL,
                    co2_level_avg REAL,
                    air_quality_avg REAL,
                    grid_stability REAL,
                    alert_count INTEGER,
                    overall_health BOOLEAN,
                    raw_data TEXT
                )
            ''')
            
            # Predictions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    prediction_type TEXT NOT NULL,
                    predicted_value REAL,
                    confidence REAL,
                    horizon_hours INTEGER,
                    actual_value REAL,
                    accuracy REAL
                )
            ''')
            
            # Insights table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS insights (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    insight_type TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    impact_score REAL,
                    recommendation TEXT
                )
            ''')
            
            self.db_connection.commit()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Analytics database initialized")
            
        except sqlite3.Error as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Database error: {e}")
    
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connected to cloud broker")
            client.subscribe(SUBSCRIBE_TOPIC, qos=1)
            client.publish(f"status/{CLIENT_ID}", "online", retain=True)
            print(f"[{CLIENT_ID}] Subscribed to: {SUBSCRIBE_TOPIC}")
            self.connected = True
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connection failed: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Disconnected")
        self.connected = False
    
    def on_message(self, client, userdata, msg):
        try:
            self.message_count += 1
            payload = msg.payload.decode()
            data = json.loads(payload)
            
            # Buffer data for analysis
            self.analytics_buffer.append(data)
            
            # Keep buffer manageable
            if len(self.analytics_buffer) > 200:
                self.analytics_buffer.pop(0)
            
            # Store in database
            self.store_analytics_data(data, payload)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Processed analytics data (Buffer: {len(self.analytics_buffer)})")
            
        except json.JSONDecodeError as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] JSON decode error: {e}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error processing message: {e}")
    
    def store_analytics_data(self, data, raw_data):
        """Store analytics data in database"""
        try:
            cursor = self.db_connection.cursor()
            
            facility_status = data.get('facility_status', {})
            energy_analytics = data.get('energy_analytics', {})
            env_analytics = data.get('environment_analytics', {})
            alerts = data.get('critical_alerts', [])
            
            cursor.execute('''
                INSERT INTO analytics_data 
                (timestamp, energy_efficiency, environmental_comfort, power_consumption_avg,
                 power_factor_avg, temperature_avg, co2_level_avg, air_quality_avg,
                 grid_stability, alert_count, overall_health, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('timestamp'),
                facility_status.get('energy_efficiency'),
                facility_status.get('environmental_comfort'),
                energy_analytics.get('power_consumption', {}).get('average') if energy_analytics else None,
                energy_analytics.get('power_factor', {}).get('average') if energy_analytics else None,
                env_analytics.get('temperature', {}).get('average') if env_analytics else None,
                env_analytics.get('co2_level', {}).get('average') if env_analytics else None,
                env_analytics.get('air_quality', {}).get('average_index') if env_analytics else None,
                energy_analytics.get('grid_stability') if energy_analytics else None,
                len(alerts),
                facility_status.get('overall_health'),
                raw_data
            ))
            
            self.db_connection.commit()
            
        except sqlite3.Error as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error storing data: {e}")
    
    def predict_energy_consumption(self, historical_data):
        """Predict future energy consumption using simple trend analysis"""
        if len(historical_data) < 5:
            return None
        
        try:
            # Extract power consumption values
            power_values = []
            timestamps = []
            
            for record in historical_data[-20:]:  # Use last 20 data points
                if record.get('power_consumption_avg'):
                    power_values.append(record['power_consumption_avg'])
                    timestamps.append(datetime.fromisoformat(record['timestamp'].replace('Z', '+00:00')))
            
            if len(power_values) < 3:
                return None
            
            # Simple linear trend calculation
            n = len(power_values)
            x_values = list(range(n))
            
            # Calculate slope (trend)
            x_mean = statistics.mean(x_values)
            y_mean = statistics.mean(power_values)
            
            numerator = sum((x_values[i] - x_mean) * (power_values[i] - y_mean) for i in range(n))
            denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
            
            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator
            
            intercept = y_mean - slope * x_mean
            
            # Predict next value
            next_value = slope * n + intercept
            
            # Calculate confidence based on variance
            variance = statistics.variance(power_values) if len(power_values) > 1 else 0
            confidence = max(0.5, 1 - (variance / (y_mean ** 2)) * 0.1) if y_mean != 0 else 0.5
            
            return {
                'predicted_value': max(0, next_value),
                'confidence': min(1.0, confidence),
                'trend': 'increasing' if slope > 0.5 else 'decreasing' if slope < -0.5 else 'stable'
            }
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error in energy prediction: {e}")
            return None
    
    def predict_maintenance_needs(self, historical_data):
        """Predict maintenance needs based on patterns"""
        if len(historical_data) < 10:
            return None
        
        try:
            # Analyze alert patterns
            recent_data = historical_data[-30:]  # Last 30 records
            alert_counts = [record.get('alert_count', 0) for record in recent_data]
            
            # Calculate alert trend
            if len(alert_counts) > 1:
                avg_alerts = statistics.mean(alert_counts)
                recent_avg = statistics.mean(alert_counts[-10:]) if len(alert_counts) >= 10 else avg_alerts
                
                # If recent alerts are significantly higher than average
                if recent_avg > avg_alerts * 1.5 and avg_alerts > 0:
                    maintenance_score = min(1.0, recent_avg / (avg_alerts * 2))
                    return {
                        'maintenance_probability': maintenance_score,
                        'recommended_action': 'preventive_maintenance' if maintenance_score > 0.7 else 'monitoring',
                        'confidence': 0.8
                    }
            
            return {
                'maintenance_probability': 0.1,
                'recommended_action': 'normal_operation',
                'confidence': 0.6
            }
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error in maintenance prediction: {e}")
            return None
    
    def generate_insights(self, historical_data):
        """Generate actionable insights from historical data"""
        insights = []
        
        if len(historical_data) < 5:
            return insights
        
        try:
            recent_data = historical_data[-20:]  # Last 20 records
            
            # Energy efficiency insights
            efficiency_values = [r.get('energy_efficiency', 0) for r in recent_data if r.get('energy_efficiency')]
            if efficiency_values:
                avg_efficiency = statistics.mean(efficiency_values)
                if avg_efficiency < 75:
                    insights.append({
                        'type': 'efficiency',
                        'category': 'energy',
                        'description': f'Energy efficiency is below optimal at {avg_efficiency:.1f}%',
                        'impact_score': 0.8,
                        'recommendation': 'Consider equipment optimization and power factor correction'
                    })
                elif avg_efficiency > 90:
                    insights.append({
                        'type': 'performance',
                        'category': 'energy',
                        'description': f'Excellent energy efficiency maintained at {avg_efficiency:.1f}%',
                        'impact_score': 0.9,
                        'recommendation': 'Continue current operational practices'
                    })
            
            # Environmental comfort insights
            comfort_values = [r.get('environmental_comfort', 0) for r in recent_data if r.get('environmental_comfort')]
            if comfort_values:
                avg_comfort = statistics.mean(comfort_values)
                if avg_comfort < 70:
                    insights.append({
                        'type': 'comfort',
                        'category': 'environment',
                        'description': f'Environmental comfort is suboptimal at {avg_comfort:.1f}%',
                        'impact_score': 0.6,
                        'recommendation': 'Review HVAC settings and air quality management'
                    })
            
            # Power consumption patterns
            power_values = [r.get('power_consumption_avg', 0) for r in recent_data if r.get('power_consumption_avg')]
            if len(power_values) > 5:
                power_variance = statistics.variance(power_values)
                if power_variance > 500:  # High variance
                    insights.append({
                        'type': 'stability',
                        'category': 'energy',
                        'description': 'High variability in power consumption detected',
                        'impact_score': 0.7,
                        'recommendation': 'Investigate load balancing and equipment cycling'
                    })
            
            # Alert frequency analysis
            alert_counts = [r.get('alert_count', 0) for r in recent_data]
            total_alerts = sum(alert_counts)
            if total_alerts > len(recent_data) * 0.5:  # More than 0.5 alerts per reading
                insights.append({
                    'type': 'reliability',
                    'category': 'maintenance',
                    'description': f'High alert frequency detected ({total_alerts} alerts in {len(recent_data)} readings)',
                    'impact_score': 0.9,
                    'recommendation': 'Schedule comprehensive system inspection'
                })
            
            return insights
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error generating insights: {e}")
            return insights
    
    def store_prediction(self, prediction_type, prediction_data):
        """Store prediction in database"""
        try:
            cursor = self.db_connection.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (timestamp, prediction_type, predicted_value, confidence, horizon_hours)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                prediction_type,
                prediction_data.get('predicted_value'),
                prediction_data.get('confidence'),
                1  # 1 hour horizon
            ))
            self.db_connection.commit()
            
        except sqlite3.Error as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error storing prediction: {e}")
    
    def store_insights(self, insights):
        """Store insights in database"""
        try:
            cursor = self.db_connection.cursor()
            for insight in insights:
                cursor.execute('''
                    INSERT INTO insights 
                    (timestamp, insight_type, category, description, impact_score, recommendation)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    insight['type'],
                    insight['category'],
                    insight['description'],
                    insight['impact_score'],
                    insight['recommendation']
                ))
            self.db_connection.commit()
            
        except sqlite3.Error as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Error storing insights: {e}")
    
    def perform_analysis(self):
        """Perform advanced analytics periodically"""
        while True:
            try:
                time.sleep(ANALYSIS_INTERVAL)
                
                # Get historical data from database
                cursor = self.db_connection.cursor()
                cursor.execute('''
                    SELECT * FROM analytics_data 
                    WHERE timestamp > datetime('now', '-2 hours')
                    ORDER BY timestamp DESC
                    LIMIT 50
                ''')
                
                historical_data = []
                for row in cursor.fetchall():
                    historical_data.append({
                        'timestamp': row[1],
                        'energy_efficiency': row[2],
                        'environmental_comfort': row[3],
                        'power_consumption_avg': row[4],
                        'power_factor_avg': row[5],
                        'temperature_avg': row[6],
                        'co2_level_avg': row[7],
                        'air_quality_avg': row[8],
                        'grid_stability': row[9],
                        'alert_count': row[10],
                        'overall_health': row[11]
                    })
                
                if len(historical_data) < 3:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Insufficient data for analysis")
                    continue
                
                # Perform predictions
                energy_prediction = self.predict_energy_consumption(historical_data)
                if energy_prediction:
                    self.store_prediction('energy_consumption', energy_prediction)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Energy prediction: "
                          f"{energy_prediction['predicted_value']:.1f} kW (confidence: {energy_prediction['confidence']:.2f})")
                
                maintenance_prediction = self.predict_maintenance_needs(historical_data)
                if maintenance_prediction:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Maintenance prediction: "
                          f"{maintenance_prediction['maintenance_probability']:.2f} probability, {maintenance_prediction['recommended_action']}")
                
                # Generate insights
                insights = self.generate_insights(historical_data)
                if insights:
                    self.store_insights(insights)
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Generated {len(insights)} insights")
                    
                    for insight in insights[:3]:  # Print top 3 insights
                        print(f"   💡 [{insight['category'].upper()}] {insight['description']}")
                
                # Database statistics
                cursor.execute('SELECT COUNT(*) FROM analytics_data')
                analytics_count = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM predictions')
                predictions_count = cursor.fetchone()[0]
                cursor.execute('SELECT COUNT(*) FROM insights')
                insights_count = cursor.fetchone()[0]
                
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Database: "
                      f"{analytics_count} analytics, {predictions_count} predictions, {insights_count} insights")
                
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Analysis error: {e}")
    
    def start(self):
        """Start the analytics engine"""
        try:
            # Set will message for clean disconnect detection
            self.client.will_set(f"status/{CLIENT_ID}", "offline", retain=True)
            
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Connecting to {BROKER}:{PORT}")
            self.client.connect(BROKER, PORT, 60)
            
            # Start MQTT loop in background
            self.client.loop_start()
            
            # Start analysis thread
            analysis_thread = threading.Thread(target=self.perform_analysis, daemon=True)
            analysis_thread.start()
            
            # Keep main thread alive
            while True:
                time.sleep(5)
                if self.message_count > 0 and self.message_count % 10 == 0:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Processed {self.message_count} analytics reports")
                
        except KeyboardInterrupt:
            print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [{CLIENT_ID}] Shutting down...")
            self.client.publish(f"status/{CLIENT_ID}", "offline", retain=True)
            self.client.disconnect()
            self.client.loop_stop()
            if self.db_connection:
                self.db_connection.close()

if __name__ == "__main__":
    analytics = AnalyticsEngine()
    analytics.start()
